#%% Imports

import napari
import numpy as np
from magicgui import magicgui
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

#%%

def display_cell_data(cell_data, all_id, myoii, pulse_data_path):

    # Define cellViewer class
    class cellViewer(napari.Viewer):
        pass

    cellViewer.cell_data = cell_data[0]
    cellViewer.pulse_idx = 0
    cellViewer.pulse_data = np.zeros((6, len(all_id)), dtype=int)
    
    # Filter myoii_intden signal
    myoii_intden = cell_data[0]['myoii_intden']
    sos = signal.butter(2, 0.3, 'low', output='sos') # lowpass IIR
    myoii_intden_filt = signal.sosfiltfilt(sos, myoii_intden)
    
    # Plot cell fig
    cell_fig = plt.figure(dpi=100) # Graph resolution
    
    # ---
    
    ax1 = cell_fig.add_subplot()
    line1, = ax1.plot(
        cell_data[0]['time_range'], cell_data[0]['myoii_intden'], 
        color=('#2378BE'), linewidth=2, zorder=2, label='MyoII'
        )
    
    line1_filt, = ax1.plot(
        cell_data[0]['time_range'], myoii_intden_filt,
        color='black', linestyle='dotted', zorder=3, label='MyoII filt'
        )
    
    ax1.set_xlabel('Time point')
    ax1.set_ylabel('MyoII Int. Den. (A.U.)')
    
    # ---
    
    ax2 = ax1.twinx()
    line2, = ax2.plot(
        cell_data[0]['time_range'], cell_data[0]['area'],
        color='0.75', zorder=1, label='area'
        ) 
    
    ax2.set_xlabel('Time point')
    ax2.set_ylabel('Cell area (pixels)')  
    
    # ---

    ax3 = ax1.twinx(); 
    ax3.axis('off')
    
    # ---
    
    ax1.set_title('Cell #' + str(1) + ' MyoII & cell area')
    ax1.legend(handles=[line1, line1_filt, line2])
    
    # ---
    
    cell_fig.tight_layout()

#%% 
    
    @magicgui(
        
        auto_call = True,
               
        current_frame = {
            'widget_type': 'Slider', 
            'label': 'current frame',
            'readout': False,
            'min': 0, 
            'value': len(cellViewer.cell_data['time_range'])//2,
            'max': len(cellViewer.cell_data['time_range'])-1
            },
        
        next_cell = {
            'widget_type': 'PushButton',
            'label': 'next cell',
            'value': False, 

            },
        
        exit_cell = {
            'widget_type': 'PushButton',
            'label': 'exit and save',
            'value': False, 

            },
        
        pulse1 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°1', 
            'value': 'ti;tf'
            },
        
        pulse2 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°2', 
            'value': 'ti;tf'
            },
        
        pulse3 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°3', 
            'value': 'ti;tf'
            },
        
        pulse4 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°4', 
            'value': 'ti;tf'
            },
        
        pulse5 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°5', 
            'value': 'ti;tf'
            },
        
        pulse6 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°6', 
            'value': 'ti;tf'
            },
        
        pulse7 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°7', 
            'value': 'ti;tf'
            },
        
        pulse8 = {
            'widget_type': 'LineEdit', 
            'label': 'pulse n°8', 
            'value': 'ti;tf'
            },
        
        )
    
#%%
    
    def display(
            current_frame: int,
            next_cell: bool,
            exit_cell: bool,
            pulse1: str,
            pulse2: str,
            pulse3: str,
            pulse4: str,
            pulse5: str,
            pulse6: str,
            pulse7: str,
            pulse8: str,
            ):    
        
        # Extract t0
        t0 = np.min(cellViewer.cell_data['time_range'])
        
        # Draw current_frame vertical line
        ax3.clear()
        ax3.axvline(x=current_frame + t0, color='black', linewidth=1)
        ax3.text(current_frame + t0 + 0.5, 0.95, f'{current_frame + t0}')
        ax3.axis('off') 
        
        # Draw graph  
        cell_fig.canvas.draw_idle()
        
#%%                

    @display.current_frame.changed.connect 
    def callback_current_frame():

        viewer.dims.set_point(0, display.current_frame.value)

    # -------------------------------------------------------------------------
    
    @display.next_cell.changed.connect  
    def callback_next_cell():
                
        # Extract variables      
        
        # Update cell data
        cellViewer.cell_data = cell_data[cellViewer.cell_data['cell_id']] 
        cell_id = cellViewer.cell_data['cell_id']
        time_range = cellViewer.cell_data['time_range']
        display = cellViewer.cell_data['display']
    
        # Update display
        viewer.layers.pop(0)
        viewer.add_image(
            display,
            name = 'Cell #' + str(cell_id) + ' MyoII',
            contrast_limits = [0, np.quantile(myoii, 0.999)]
            )
        
        # Update graph
        line1.set_xdata(time_range)
        line1.set_ydata(cellViewer.cell_data['myoii_intden'])
        ax1.relim()
        ax1.autoscale_view()
        
        line2.set_xdata(time_range)
        line2.set_ydata(cellViewer.cell_data['area'])
        ax2.relim()
        ax2.autoscale_view()
        
        ax1.set_title('Cell #' + str(cell_id) + ' MyoII & cell area')
        
        # Update current frame slider
        display.current_frame.value = len(cellViewer.cell_data['time_range'])//2
        display.current_frame.max = len(cellViewer.cell_data['time_range'])-1
        
    # -------------------------------------------------------------------------     
    
    @display.exit_cell.changed.connect  
    def callback_exit_cell():
        
        np.savetxt(pulse_data_path, cellViewer.pulse_data, fmt='%i', delimiter=',')
        cellViewer.close(viewer)

#%%
    
    # Set up the viewer
    viewer = cellViewer()
    display.native.layout().addWidget(FigureCanvas(cell_fig)) 
    viewer.window.add_dock_widget(display, area='right', name='widget') 
    viewer.add_image(
        cell_data[0]['display'],
        name='Cell #' + str(1) + ' MyoII',
        contrast_limits = [0, np.quantile(myoii, 0.999)]
        )

    # -------------------------------------------------------------------------   
    
    @viewer.bind_key('Enter')
    def add_pulse_info(viewer):
        
        # Extract variables
        t0 = np.min(cellViewer.cell_data['time_range'])
        pulse_idx = cellViewer.pulse_idx + 1      
        pulse_number = np.ceil(pulse_idx/2)
        current_frame = display.current_frame.value + t0
        
        if (pulse_idx % 2) != 0:
            pulse_t = 'ti'
        else:
            pulse_t = 'tf'
            
        # Update variables   
        cellViewer.pulse_idx = pulse_idx
        display.pulse1.value = display.pulse1.value.replace(pulse_t, str(current_frame)) 
        # setattr(display, 'pulse', 1).value = display.pulse1.value.replace(pulse_t, str(current_frame)) 
        print(f'idx={pulse_idx} pulse n°{int(pulse_number)} {pulse_t}={current_frame}') 
        
    @viewer.bind_key('Backspace')
    def remove_pulse_info(viewer):
        
        if cellViewer.pulse_idx > 1:
        
            # Extract variables
            t0 = np.min(cellViewer.cell_data['time_range'])
            pulse_idx = cellViewer.pulse_idx - 1      
            pulse_number = np.ceil(pulse_idx/2)
            current_frame = display.current_frame.value + t0
                
            if (pulse_idx % 2) != 0:
                pulse_t = 'ti'
            else:
                pulse_t = 'tf'    
                
            # Update variables   
            cellViewer.pulse_idx = pulse_idx
                
            print(f'idx={pulse_idx} pulse n°{int(pulse_number)} {pulse_t}={current_frame}') 
    
    return cellViewer.pulse_data


    
