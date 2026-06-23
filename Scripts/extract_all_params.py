import os
import glob
import re
import csv

DATA_ROOT = r"c:\Users\lenovo\Desktop\FRB-capstone\Google_Drive_Data_Package"

# Defined Order from Guide
GALAXIES = [
    "NGC_5846", # E0
    "NGC_5576", # E3
    "NGC_4623", # E7
    "NGC_3245", # S0
    "NGC_4762", # S0
    "NGC_4378", # Sa
    "NGC_4814", # Sb
    "NGC_3938"  # Sc
]

# Map specific "Best" logs for With PSF case
LOG_MAP_WITH_PSF = {
    "NGC_5846": "NGC_5846_fit_withpsf_multi_fixedsky.log",
    "NGC_5576": "NGC_5576_fit_withpsf_multi.log",
    "NGC_4762": "NGC_4762_fit_withpsf_n5.log",
    # Others default to standard
}

# Map specific "Best" logs for No PSF case
LOG_MAP_NO_PSF = {
    "NGC_5846": "NGC_5846_fit_nopsf_multi_fixedsky.log",
    "NGC_5576": "NGC_5576_fit_nopsf_multi.log",
    # Others default to standard
}

def parse_galfit_log(log_path):
    params = {}
    try:
        with open(log_path, 'r') as f:
            content = f.read()
            
        # Chi2/nu
        chi2_match = re.search(r"Chi\^2/nu\s*=\s*([\d\.]+)", content)
        if chi2_match:
            params['chi2_nu'] = float(chi2_match.group(1))
            
        # Components - looking for "sersic" blocks
        # This is a bit tricky with regex, simpler to iterate lines
        lines = content.splitlines()
        components = []
        current_comp = {}
        
        for i, line in enumerate(lines):
            if "sersic" in line:
                # Start of component
                # Next line has position
                # Next has mag
                # Next has Re (col 4)
                # Next has n (col 5)
                # Next has b/a (col 9)
                try:
                    re_line = lines[i+3] # Line with Re is typically 3 lines down ? No, let's look at structure
                    # Line 8: sersic : (x, y) mag re n b/a pa
                    #Wait, format in log:
                    # sersic : (x,y) mag re n b/a pa
                    #          (errs) ...
                    # Actually standard log has params in columns on the same line "sersic :"
                    parts = line.split()
                    # index 0: sersic
                    # index 1: :
                    # index 2: (x
                    # index 3: y)
                    # index 4: mag
                    # index 5: Re
                    # index 6: n
                    # index 7: b/a
                    # index 8: pa
                    
                    comp = {
                        'mag': float(parts[4]),
                        're': float(parts[5]),
                        'n': float(parts[6]),
                        'ba': float(parts[7]),
                        'pa': float(parts[8])
                    }
                    if '[' in parts[6]: # Fixed param check
                         comp['n_fixed'] = True
                         comp['n'] = float(parts[6].replace('[','').replace(']',''))
                    else:
                         comp['n_fixed'] = False

                    components.append(comp)
                except:
                    pass
        
        params['components'] = components
        return params

    except Exception as e:
        print(f"Error parsing {log_path}: {e}")
        return None

def extract_all():
    results = []
    
    for gal in GALAXIES:
        gal_dir = os.path.join(DATA_ROOT, gal)
        
        # --- With PSF ---
        log_name_psf = LOG_MAP_WITH_PSF.get(gal, f"{gal}_fit_withpsf.log")
        log_path_psf = os.path.join(gal_dir, log_name_psf)
        
        # --- No PSF ---
        log_name_nopsf = LOG_MAP_NO_PSF.get(gal, f"{gal}_fit_nopsf.log")
        log_path_nopsf = os.path.join(gal_dir, log_name_nopsf)
        
        data = {'galaxy': gal}
        
        if os.path.exists(log_path_psf):
            data['psf'] = parse_galfit_log(log_path_psf)
        else:
            print(f"Missing PSF Log: {log_path_psf}")
            
        if os.path.exists(log_path_nopsf):
            data['nopsf'] = parse_galfit_log(log_path_nopsf)
        else:
            print(f"Missing No-PSF Log: {log_path_nopsf}")
            
        results.append(data)
        
    return results

if __name__ == "__main__":
    res = extract_all()
    # Print as simple text block for me to read and format into MD
    for r in res:
        print(f"\n=== {r['galaxy']} ===")
        # No PSF
        if 'nopsf' in r and r['nopsf']:
            p = r['nopsf']
            print(f"No PSF: Chi2={p.get('chi2_nu', 'N/A')}")
            for i, c in enumerate(p.get('components', [])):
                print(f"  Comp {i+1}: n={c['n']:.2f}, Re={c['re']:.2f}, b/a={c['ba']:.2f}, mag={c['mag']:.2f}")
                
        # With PSF
        if 'psf' in r and r['psf']:
            p = r['psf']
            print(f"With PSF: Chi2={p.get('chi2_nu', 'N/A')}")
            for i, c in enumerate(p.get('components', [])):
                print(f"  Comp {i+1}: n={c['n']:.2f}, Re={c['re']:.2f}, b/a={c['ba']:.2f}, mag={c['mag']:.2f}")

