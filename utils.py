"""Utilities for the evaluation of the pore volume."""
from numpy import mean
import matplotlib.pyplot as plt

GAS_MMASS = { #g/mol
    'Nitrogen': 14.01*2,
    'Argon': 39.948,
    'Carbon Dioxide': 44.01,
}

LIQ_DENS = { # https://webbook.nist.gov/chemistry/fluid/
    'N2@77K': 28.833, # (mmol/cm3) @ 1bar, 77K
    'Ar@87K': 34.977  # (mmol/cm3) @ 1bar, 87K
}

def adsorption_units_conversion(adsorptionUnits, gas):
    """Convert any loading to mmol/g, i.e., millimole of adsorbate (gas) per gram of adsorbent (mat)."""
    
    if adsorptionUnits == 'wt%': # let's consider it as gas/mat_empty
        adsorptionUnits = 'g/hg'
    
    if len(adsorptionUnits.split("/"))==2:
        gas_unit, mat_unit = adsorptionUnits.split("/")
    else:
        raise ValueError('adsorptionUnit has wrong format: {}'.format(adsorptionUnits))

    conv = 1
    if gas_unit == 'mmol': 
        conv *= 1
    elif gas_unit == 'mol': 
        conv *= 1000
    elif gas_unit in ['cm3(STP)', 'ml']: # assuming ml(STP) 
        conv *= 1/22.414
    elif gas_unit == 'g': 
        conv *= 1/GAS_MMASS[gas]*1000
    elif gas_unit == 'mg': 
        conv *= 1/GAS_MMASS[gas]
    else: 
        raise ValueError('adsorptionUnit has weird gas unit: {}'.format(adsorptionUnits))

    if mat_unit == 'g':
        conv *= 1
    elif mat_unit == 'mg':
        conv *= 1000
    elif mat_unit == 'hg':
        conv *= 1/100
    elif mat_unit == 'kg':
        conv *= 1/1000  
    else: 
        raise ValueError('adsorptionUnit has wrong format: {}'.format(adsorptionUnits))
        
    #print(adsorptionUnits, end=" ")

    return conv

def isot_pore_volume(isot, comp_density, comp_porevol, plot=False):
    """Given an N2/Ar isotherms compute the pore volume (cm3/g).
    If not an isotherms of N2@77K or Ar@87K will raise an error.
    If plot=True, plots a graph of the pore volume, and also the geom/poav pore volumes.
    
    mat_dict has the keys: "pore_vol_geom" and "density" (list for all the structures).
    """


    
    if isot['adsorbates'][0]['name']=='Nitrogen' and isot['temperature']==77:
        case = 'N2@77K'
    elif isot['adsorbates'][0]['name']=='Argon' and isot['temperature']==87:
        case = 'Ar@87K'
    else:
        raise ValueError("Molecule/temperature unknown for pore characterization.")

    # conv adsorptionUnits to mmol/g
    conv = adsorption_units_conversion(isot['adsorptionUnits'], isot['adsorbates'][0]['name'])
    
    # For the moment I'm just making a simple average of all the points in the 0.2-0.8 bar range
    thr_press = (0.58, 0.82) # (bar) ADJUST IT!
    range_press = []
    range_uptake = []
    for isot_data in isot['isotherm_data']:
        if thr_press[0]<isot_data['pressure']<thr_press[1]:
            range_press.append(isot_data['pressure'])
            range_uptake.append(isot_data['species_data'][0]['adsorption'])
            
    pore_vol = float(mean(range_uptake) * conv / LIQ_DENS[case]) # (cm3/g)
    
    if plot:
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=[12,5])
        
        # First plot: original units in full scale
        ax1.set_xlabel('Pressure (bar)')
        ax1.set_ylabel(f"{case} uptake {isot['adsorptionUnits']}")
        # Plot full isotherm and points used to compute the pore volume
        x = [isot_data['pressure'] for isot_data in isot['isotherm_data']]
        y = [isot_data['species_data'][0]['adsorption'] for isot_data in isot['isotherm_data']]
        ax1.plot(x, y, color="blue", marker="o", markersize=3)
        ax1.plot(range_press, range_uptake, marker="o", markersize=6, color="blue")
        ax1.tick_params(axis='y')
        ax1.set_ylim(0,max(y)*1.1)

        # Second plot, left axis: original units, scaled axis to vf=1
        ax2.set_xlabel('Pressure (bar)')
        ax2.set_ylabel(f"{case} uptake {isot['adsorptionUnits']}")
        ax2.plot(x, y, color="blue", marker="o", markersize=4, label="Isotherm")
        ax2.plot(range_press, range_uptake, marker="o", markersize=4, color="red")
        ax2.set_ylim(0,LIQ_DENS[case]/comp_density/conv) # Scale to equivalent to void fraction = 1 
           
        # Seconf plot, right axis: Void Fraction
        ax3 = ax2.twinx()  
        ax3.set_ylabel('Void fraction')  # we already handled the x-label with ax1              
        ax3.plot([0,1],[pore_vol*comp_density]*2, color='red', label='Measured Void Fract.')
        ax3.plot([0,1],[comp_density*comp_porevol]*2, color='green', label='Geometric Void Fract')
        print(pore_vol*comp_density, comp_density*comp_porevol)
        ax3.set_ylim(0,1)
        ax3.legend()

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
    
    return pore_vol