import time
init_st = time.time() * 1000
import matplotlib
import matplotlib.pyplot as plt
init_ed = time.time() * 1000
matplotlib.use('Agg')

def handle(req):
    # Data for plotting
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 25, 30, 40]

    # Create a plot
    plt.plot(x, y, label='Line 1')

    # Add labels and title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Basic Plot')

    # Add legend
    plt.legend()

    # Save the plot to a file
    plt.savefig('plot.png')  # Saves as a PNG file in the current directory
    plt.close()  # Close the plot to free memory
    return f'latency is {init_ed - init_st}ms'