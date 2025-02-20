import numpy as np
import matplotlib.pyplot as plt
import cv2

def generate_heatmap(temperature_array, output_filename="heatmap.png"):
    # Ensure the input is a 2D array with shape (24, 32)
    if temperature_array.shape != (24, 32):
        raise ValueError("Input array must have shape (24, 32)")
    
    # Determine the actual min and max temperature values
    min_temp = 10
    max_temp = 50
    
    # Normalize the temperature values to range [0, 255]
    norm_temp = ((temperature_array - min_temp) / (max_temp - min_temp) * 255).astype(np.uint8)
    
    # Apply infrared colormap
    heatmap = cv2.applyColorMap(norm_temp, cv2.COLORMAP_INFERNO)
    
    # Resize to make the image more visible while maintaining resolution
    heatmap_resized = cv2.resize(heatmap, (380, 290), interpolation=cv2.INTER_NEAREST)
    
    # Add a white border
    border_size = 10
    heatmap_with_border = cv2.copyMakeBorder(
        heatmap_resized, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cv2.cvtColor(heatmap_with_border, cv2.COLOR_BGR2RGB))
    ax.axis("off")
    
    # Add a colorbar (legend) with correct temperature values
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap='inferno', norm=plt.Normalize(vmin=min_temp, vmax=max_temp)), ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Temperature (°C)")
    tick_values = np.linspace(min_temp, max_temp, num=5)
    cbar.set_ticks(tick_values)
    cbar.set_ticklabels([str(int(round(tick))) for tick in tick_values])
    
    # Save the image
    plt.savefig(output_filename, bbox_inches='tight')

    plt.close(fig)
    

# Example usage
temp_data = np.random.uniform(20, 100, (24, 32))  # Generate random temperatures between 20°C and 100°C
generate_heatmap(temp_data)
