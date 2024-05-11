import numpy as np  
import os  
  
# Define the folder path to the original ASC file and the output folder path to the new ASC file
original_asc_dir = 'your MEIC.asc path\\'  
resized_asc_dir = 'your output path\\'  
  
# Make sure the output folder exists  
if not os.path.exists(resized_asc_dir):  
    os.makedirs(resized_asc_dir)  
  
# Walk through all ASC files in the folder
for filename in os.listdir(original_asc_dir):  
    if filename.endswith('.asc'):  
        original_asc_path = os.path.join(original_asc_dir, filename)  
        new_asc_filename = filename.replace('.asc', '_resized.asc')  
        new_asc_path = os.path.join(resized_asc_dir, new_asc_filename)  
          
        with open(original_asc_path, 'r') as f:  
            header = []  
            for line in f:  
                if line.strip() == 'DATA':  
                    break  
                header.append(line.strip())  
         
        # Parse header file information  
        ncols_original = int(header[0].split()[1])  
        nrows_original = int(header[1].split()[1])  
        xllcorner = float(header[2].split()[1])  
        yllcorner = float(header[3].split()[1])  
        original_cellsize = float(header[4].split()[1])  
        NODATA_value = float(header[5].split()[1])   
          
        # Initial conversion, from raw cellsize to 0.05  
        new_cellsize = 0.05  
        new_nrows = int(nrows_original * (original_cellsize / new_cellsize))  
        new_ncols = int(ncols_original * (original_cellsize / new_cellsize))  
        # Read raw data  
        data = np.loadtxt(original_asc_path, skiprows=6)  
        data = data.reshape((nrows_original, ncols_original))  
  
        # Initialize the new data array and fill it with NODATA_value  
        #new_data = np.full((new_nrows, new_ncols), NODATA_value) 
        new_data = np.full((new_nrows, new_ncols), NODATA_value, dtype=float)  

        cell_area_ratio = (original_cellsize / new_cellsize) ** 2
        
        # Assign values to a new data array 
        for i in range(nrows_original):  
            for j in range(ncols_original):  
                if data[i, j] != NODATA_value:  
                    num_new_cells = int(cell_area_ratio)
                    new_value_per_cell = data[i, j] / num_new_cells  
                    start_i = int(i * (new_nrows / nrows_original))  
                    end_i = int((i + 1) * (new_nrows / nrows_original))  
                    start_j = int(j * (new_ncols / ncols_original))  
                    end_j = int((j + 1) * (new_ncols / ncols_original))  
                    new_data[start_i:end_i, start_j:end_j][new_data[start_i:end_i, start_j:end_j] == NODATA_value] = new_value_per_cell  
          
        # Second conversion, from 0.05 to 0.1 
        new_cellsize_2 = 0.1  
        new_nrows_2 = int(new_nrows * (new_cellsize / new_cellsize_2))  
        new_ncols_2 = int(new_ncols * (new_cellsize / new_cellsize_2))  
        new_data_2 = np.full((new_nrows_2, new_ncols_2), NODATA_value, dtype=float)  
          
        for i_new in range(new_nrows_2):  
            for j_new in range(new_ncols_2):  
                i_start = int(i_new * 2)  
                i_end = int(i_start + 2)  
                j_start = int(j_new * 2)  
                j_end = int(j_start + 2)
                # Extract 4 adjacent cells from the original data 
                values = new_data[i_start:i_end, j_start:j_end]  
                values = values[values != NODATA_value]  

                # If there is valid data in these cells, calculate their sum
                if values.size > 0:  
                    new_value = np.sum(values)  
                    new_data_2[i_new, j_new] = new_value  

        # Write a new ASC file  
        with open(new_asc_path, 'w') as f:  
            f.write('ncols {}\n'.format(new_ncols_2))  
            f.write('nrows {}\n'.format(new_nrows_2))  
            f.write('xllcorner {}\n'.format(xllcorner))  
            f.write('yllcorner {}\n'.format(yllcorner))  
            f.write('cellsize {}\n'.format(new_cellsize_2))  
            f.write('NODATA_value {}\n'.format(NODATA_value))  

            for row in new_data_2:  
                f.write(' '.join(map(str, row)) + '\n')  

        print("Resized ASC file has been saved to:", new_asc_path)