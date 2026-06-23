import matplotlib.pyplot as plt

# Data from clean_6_summary.md
# Columns: Galaxy, Type, Model Config, Chi2/nu, n (No PSF), n (With PSF), Bulge Re (px), Disk Re (px), Notes
columns = ["Galaxy", "Type", "Model Config", "Chi2/nu", "n (No PSF)", "n (With PSF)", "Bulge Re", "Disk Re", "Notes"]
data = [
    ["NGC 3245", "S0", "2-Comp (Linked)", "12.80", "1.40", "1.73", "16.6", "132.7", "Stable: 'n' increased"],
    ["NGC 3938", "Sc", "2-Comp (Fixed)", "20.50", "1.19", "1.27", "23.9", "249.7", "Stable: Smooth spiral"],
    ["NGC 4378", "Sa", "2-Comp (Fixed)", "8.16", "2.84", "4.13", "30.2", "135.5", "Massive PSF Impact"],
    ["NGC 4623", "E7", "2-Comp (Fixed n)", "12.13", "3.30", "4.00 (Fixed)", "77.2", "118.2", "Degeneracy Fixed (n=4)"],
    ["NGC 4762", "S0", "2-Comp (Fixed n)", "30.29", "4.69", "4.00 (Fixed)", "49.5", "269.9", "Fixed n=4 favored"],
    ["NGC 4814", "Sb", "2-Comp (Fixed n)", "10.69", "3.26", "4.00 (Fixed)", "112.1", "82.3", "Degeneracy Fixed (n=4)"]
]

# Plotting
fig, ax = plt.subplots(figsize=(14, 5)) # Size suitable for a wide table
ax.axis('tight')
ax.axis('off')

# Design Table
# cellText takes a list of lists
table = ax.table(cellText=data, colLabels=columns, cellLoc='center', loc='center', bbox=[0, 0, 1, 1])

# Styling
table.auto_set_font_size(False)
table.set_fontsize(11)

# Color coding headers and rows
# get_celld() returns a dict of (row, col): cell
cells = table.get_celld()
for i in range(len(data) + 1): # +1 for header
    for j in range(len(columns)):
        cell = cells[(i, j)]
        
        # Header Row
        if i == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e') # Dark blue header
            cell.set_height(0.12)
        else:
            # Data Rows
            # Alternating row colors
            if i % 2 == 0:
                cell.set_facecolor('#f2f2f2')
            else:
                cell.set_facecolor('white')
            
            # Highlight "Fixed n" rows (Column 2 check)
            # data is 0-indexed, so row i maps to data[i-1]
            if "Fixed n" in data[i-1][2]:
                 if j == 2: # Model Config column
                     cell.set_facecolor('#fffacc')
                     cell.set_text_props(weight='bold')
            
            # Highlight significant "n" increases (Column 5 check)
            # Safe float conversion
            try:
                val_no = float(data[i-1][4])
                val_with_str = data[i-1][5].split()[0] # Handle "4.00 (Fixed)"
                val_with = float(val_with_str)
                
                if j == 5 and val_with > val_no + 0.5: 
                     cell.set_text_props(weight='bold', color='#006400') # Dark green text
            except ValueError:
                pass

plt.title("Phase 3a: Clean 6 Galaxy Morphology Summary", fontsize=16, weight='bold', pad=20)
plt.tight_layout()

# Save
output_path = "clean_6_summary_graphic.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Graphic saved to {output_path}")
