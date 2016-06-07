"""
    Purpose:
        Main program set to create a flight planning software
        Is used as a basis of the interface between an excel spreadsheet
            and a clickable map
        It is to create flight lines saved to kml, txt, xls, and others.
    Inputs: 
        test: if set to true, then command line is still useable
    Outputs:
        lines: linebuilder class object
        ui: specil ui to hold the gui interface objects
    Dependencies:
        numpy
        Tkinter
        datetime
        map_utils
        excel_interface
        map_interactive
        gui
        Basemap
        PIL (through scipy.misc.imread)
        OWSLib
    Required files:
        labels.txt: file with labels of locations
        aeronet_locations.txt: file with location of aeronet sites
        arc.ico: icon for main window
    Example:
        ...
    Modification History:
        Written: Samuel LeBlanc, 2015-08-07, Santa Cruz, CA
                Copyright 2015 Samuel LeBlanc
        Modified: Samuel LeBlanc, 2015-09-02, NASA Ames, Santa Cruz, CA
                - added new buttons
                - changed imports to be more specific and not import everything
        Modified: Samuel LeBlanc, 2015-09-10, NASA Ames, Santa Cruz, CA
                - added multi plane capabilities via radiobuttons in the gui interface
        Modified: Samuel LeBlanc, 2015-09-16, NASA Ames
                - added icon in main figure
                - added move points buttons
                - added basemap creation questions
                - added GEOS imagerys with WMS service
"""

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import Tkinter as tk
import numpy as np
from mpl_toolkits.basemap import Basemap
import datetime
#import scipy, scipy.misc, scipy.special, scipy.integrate
import PIL
import re, copy
import ephem

import urllib2, socket, _socket, _ssl, _elementtree
import pykml, simplekml, pyexpat
import gpxpy, gpxpy.gpx

import map_utils as mu
import excel_interface as ex
import map_interactive as mi
import gui

import tkSimpleDialog, tkFileDialog, tkMessageBox
import owslib, owslib.wms, owslib.util
from xlwings import Range, Sheet, Workbook
import Pysolar, Pysolar.solar
import win32com, win32com.client
import FileDialog
import six, six.moves


__version__ = 'v0.8beta'

def Get_basemap_profile():
    'Program to load profile dict basemap values'
    filename = 'profiles.txt'
    defaults = Get_default_profile(filename)
    select = gui.Select_profile(defaults)
    return select.profile

def Get_default_profile(filename):
    """
    Program to try and read a text file with the default profiles
    If unavailable use some hardcoded defaults
    """
    profile = []
    try:
        f = open(filename,'r')
        dd = None
        for line in f:
            if not dd:
                first = True
                dd = line
            else:
                first = False
            if ('{' in dd) & ('}' in dd):
                profile.append(eval(dd.strip()))
                dd = line.strip()
            else:
                if first: 
                    dd = line.strip()
                else:
                    dd = ''.join((dd.strip(),line.strip()))
        profile.append(eval(dd.strip()))
    except:
        profile = [{'Profile':'ORACLES','Plane_name':'P3',
                     'Start_lon':'14 38.717E','Start_lat':'22 58.783S',
                     'Lon_range':[-20,20],'Lat_range':[-30,10],
                     'UTC_start':7.0,'UTC_conversion':+1.0,
                     'start_alt':95.0},
                    {'Profile':'NAAMES','Plane_name':'C130',
                     'Start_lon':'52 44.547W','Start_lat':'47 37.273N',
                     'Lon_range':[-55,-20],'Lat_range':[40,60],
                     'UTC_start':8.5,'UTC_conversion':-2.5,
                     'start_alt':110.0},
                    {'Profile':'KORUS-AQ','Plane_name':'DC8',
                     'Start_lon':'126 47.663E','Start_lat':'37 33.489N',
                     'Lon_range':[120,135],'Lat_range':[20,40],
                     'UTC_start':8.5,'UTC_conversion':+9,
                     'start_alt':20.0},
                    {'Profile':'AJAX','Plane_name':'Alpha-jet',
                     'Start_lon':'122 3.489W','Start_lat':'37 24.387N',
                     'Lon_range':[-125,-115],'Lat_range':[30,40],
                     'UTC_start':20.0,'UTC_conversion':+7,
                     'start_alt':95.0}]
    return profile
        
def Create_gui(vertical=True):
    'Program to set up gui interaction with figure embedded'
    class ui:
        pass
    ui = ui
    ui.root = tk.Tk()
    ui.root.wm_title('Flight planning by Samuel LeBlanc, NASA Ames, '+__version__)
    ui.root.geometry('900x950')
    try:
        ui.root.iconbitmap('arc.ico')
    except:
        pass
    ui.top = tk.Frame(ui.root)
    ui.bot = tk.Frame(ui.root)
    if vertical:
        ui.top.pack(side=tk.LEFT,expand=False)
        ui.bot.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
    else:
        ui.top.pack(side=tk.TOP,expand=False)
        ui.bot.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
    ui.fig = Figure()
    ui.ax1 = ui.fig.add_subplot(111)
    ui.canvas = FigureCanvasTkAgg(ui.fig,master=ui.root)
    ui.canvas.show()
    ui.canvas.get_tk_widget().pack(in_=ui.bot,side=tk.BOTTOM,fill=tk.BOTH,expand=1)
    ui.tb = NavigationToolbar2TkAgg(ui.canvas,ui.root)
    ui.tb.pack(in_=ui.bot,side=tk.BOTTOM)
    ui.tb.update()
    ui.canvas._tkcanvas.pack(in_=ui.bot,side=tk.TOP,fill=tk.BOTH,expand=1)
    return ui

def build_buttons(ui,lines,vertical=True):
    'Program to set up the buttons'
    import gui
    import Tkinter as tk
    from matplotlib.colors import cnames
    if vertical:
        side = tk.TOP
        h = 2
        w = 20
    else:
        side = tk.LEFT
        h = 20
        w = 2
    g = gui.gui(lines,root=ui.root,noplt=True)
    g.refresh = tk.Button(g.root,text='Refresh',
                          command=g.refresh,
                          bg='chartreuse')
    g.bopenfile = tk.Button(g.root,text='Open Excel file',
                            command=g.gui_open_xl)
    g.bsavexl = tk.Button(g.root,text='Save Excel file',
                          command=g.gui_save_xl)
    g.bsavetxt = tk.Button(g.root,text='Save text file',
                          command=g.gui_save_txt)
    g.bsaveas2kml = tk.Button(g.root,text='SaveAs to Kml',
                              command=g.gui_saveas2kml)
    g.bsave2kml = tk.Button(g.root,text='Update Kml',
                            command=g.gui_save2kml)
    g.bsave2gpx = tk.Button(g.root,text='Save to GPX',
                            command=g.gui_save2gpx)
    g.bsave2ict = tk.Button(g.root,text='Save to ICT',
			    command=g.gui_save2ict)
    g.refresh.pack(in_=ui.top,side=side,fill=tk.X,pady=8)
    tk.Label(g.root,text='File options').pack(in_=ui.top,side=side) 
    g.bopenfile.pack(in_=ui.top,side=side)
    g.bsavexl.pack(in_=ui.top,side=side)
    g.bsavetxt.pack(in_=ui.top,side=side)
    g.bsaveas2kml.pack(in_=ui.top,side=side)
    g.bsave2kml.pack(in_=ui.top,side=side)
    g.bsave2gpx.pack(in_=ui.top,side=side)
    g.bsave2ict.pack(in_=ui.top,side=side)
    tk.Frame(g.root,height=h,width=w,bg='black',relief='sunken'
             ).pack(in_=ui.top,side=side,padx=8,pady=5)
    tk.Label(g.root,text='Other plots').pack(in_=ui.top,side=side)
    g.bplotalt = tk.Button(g.root,text='Plot alt vs time',
                           command=g.gui_plotalttime)
    g.bplotalt.pack(in_=ui.top,side=side)
    g.bplotsza = tk.Button(g.root,text='Plot SZA',
                           command=g.gui_plotsza)
    g.bplotsza.pack(in_=ui.top,side=side)
    tk.Frame(g.root,height=h,width=w,bg='black',relief='sunken'
             ).pack(in_=ui.top,side=side,padx=8,pady=5)
    g.frame_select = tk.Frame(g.root,relief=tk.SUNKEN,bg='white')
    g.frame_select.pack(in_=ui.top,side=side,fill=tk.BOTH)
    tk.Label(g.root,text='Flight paths:',bg='white').pack(in_=g.frame_select,side=side)
    g.newflight_off = False
    g.flightselect_arr = []
    g.flightselect_arr.append(tk.Radiobutton(g.root,text=lines.ex.name,
                                             fg=lines.ex.color,
                                             variable=g.iactive,value=0,
                                             indicatoron=0,
                                             command=g.gui_changeflight,
                                             state=tk.ACTIVE,bg='white'))
    g.flightselect_arr[0].pack(in_=g.frame_select,side=side,padx=4,pady=2,fill=tk.BOTH)
    g.flightselect_arr[0].select()
    g.iactive.set(0)
    g.newflightpath = tk.Button(g.root,text='New flight path',
                                command = g.gui_newflight)
    g.newflightpath.pack(in_=ui.top,padx=5,pady=2)
    #g.removeflightpath = tk.Button(g.root,text='Remove flight path',
    #                               command = g.gui_removeflight)
    #g.removeflightpath.pack(in_=ui.top,padx=5,pady=5)
    g.addpoint = tk.Button(g.root,text='Add point dialog',
                           command = g.gui_addpoint)
    g.addpoint.pack(in_=ui.top,padx=5,pady=2)
    g.movepoints = tk.Button(g.root,text='Move points',
                             command = g.gui_movepoints)
    g.movepoints.pack(in_=ui.top,padx=5,pady=2)
    tk.Frame(g.root,height=h,width=w,bg='black',relief='sunken'
             ).pack(in_=ui.top,side=side,padx=8,pady=5)
    tk.Label(g.root,text='Extra info:').pack(in_=ui.top,side=side)
    g.baddsat = tk.Button(g.root,text='Add Satellite tracks',
                         command = g.gui_addsat_tle)
    g.baddsat.pack(in_=ui.top)
    g.baddbocachica = tk.Button(g.root,text='Add Forecast\nfrom Bocachica',
                         command = g.gui_addbocachica)
    g.baddbocachica.pack(in_=ui.top)
    g.baddfigure = tk.Button(g.root,text='Add Forecast\nfrom image',
                         command = g.gui_addfigure)
    g.baddfigure.pack(in_=ui.top)
    #g.baddgeos = tk.Button(g.root,text='Add GEOS',
    #                     command = g.gui_addgeos)
    #g.baddgeos.pack(in_=ui.top)
    tk.Frame(g.root,height=h,width=w,bg='black',relief='sunken'
             ).pack(in_=ui.top,side=side,padx=8,pady=5)
    tk.Button(g.root,text='Quit',command=g.stopandquit,bg='lightcoral'
              ).pack(in_=ui.top,side=side)
    ui.g = g

def get_datestr(ui):
    import tkSimpleDialog
    from datetime import datetime
    import re
    ui.datestr = tkSimpleDialog.askstring('Flight Date','Flight Date (yyyy-mm-dd):')
    if not ui.datestr:
        ui.datestr = datetime.utcnow().strftime('%Y-%m-%d')
    else:
        while not re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}',ui.datestr):
            ui.datestr = tkSimpleDialog.askstring('Flight Date',
                                                  'Bad format, please retry!\nFlight Date (yyyy-mm-dd):')
            if not ui.datestr:
                ui.datestr = datetime.utcnow().strftime('%Y-%m-%d')
    ui.ax1.set_title(ui.datestr)

def savetmp(ui,wb):
    import tempfile, os
    tmpfilename = os.path.join(tempfile.gettempdir(),ui.datestr+'.xlsx')
    try:
        wb.save2xl(tmpfilename)
    except:
        print 'unable to save excel to temp file:'+tmpfilename
        print 'continuing ...'

def init_plot(m,start_lon='14 38.717E',start_lat='22 58.783S',color='red'):
    lat0,lon0 = mi.pll(start_lat), mi.pll(start_lon)
    x0,y0 = m(lon0,lat0)
    line, = m.plot([x0],[y0],'o-',color=color,linewidth=3)
    text = ('Press s to stop interaction\\n'
            'Press i to restart interaction\\n')
    return line

def stopandquit():
    'simple function to handle the stop and quit'
    lines.ex.wb.close()
    ui.root.quit()
    ui.root.destroy()
    
def goto_cwd():
    'Program that changes the current directory to the path of the script: for use in finding extra files'
    from os.path import dirname, realpath
    from os import chdir
    from sys import argv
    if __file__:
        path = dirname(realpath(__file__))
    else:
        path = dirname(realpath(argv[0]))
    chdir(path)

def Create_interaction(test=False,profile=None,**kwargs):
    goto_cwd()
    ui = Create_gui()
    ui.tb.set_message('Creating basemap')
    profile = Get_basemap_profile()
    m = mi.build_basemap(ax=ui.ax1,profile=profile)
    if profile:
        sla,slo = profile['Start_lat'],profile['Start_lon']
    else:
        sla,slo = None,None
    line = init_plot(m,start_lat=sla,start_lon=slo,color='red')

    flabels = 'labels.txt'
    faero = 'aeronet_locations.txt'
    try:
        ui.tb.set_message('putting labels and aeronet')
        mi.plot_map_labels(m,flabels)
        mi.plot_map_labels(m,faero,marker='*',skip_lines=2,color='y')
    except:
        print 'Label files not found!'
        
    get_datestr(ui)
    ui.tb.set_message('making the Excel connection')
    wb = ex.dict_position(datestr=ui.datestr,color=line.get_color(),profile=profile,version=__version__,**kwargs)
    ui.tb.set_message('Building the interactivity on the map')
    lines = mi.LineBuilder(line,m=m,ex=wb,tb=ui.tb,blit=True)
    ui.tb.set_message('Saving temporary excel file')
    savetmp(ui,wb)
    
    build_buttons(ui,lines)
    lines.get_bg(redraw=True)
    ui.tb.set_message('Ready for interaction')
    def stopandquit():
        'simple function to handle the stop and quit'
        lines.ex.wb.close()
        ui.root.quit()
        ui.root.destroy()

    ui.root.protocol('WM_DELETE_WINDOW',stopandquit)
    if not test:
        ui.root.mainloop()
    return lines,ui

if __name__ == "__main__":
    lines,ui = Create_interaction(test=True)

