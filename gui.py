import tkinter as tk
import tkinter.filedialog as fd
from voronoi import Voronoi, Point

class MainWindow:
    # radius of drawn points on canvas
    RADIUS = 3

    # color constants
    POINT_COLOR = "black"
    LINE_COLOR = "blue"
    CIRCLE_COLOR = "green"

    # flag to lock the canvas when drawn
    LOCK_FLAG = False
    
    def __init__(self, master):
        self.master = master
        self.master.title("Voronoi")

        self.main_frame = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.main_frame, width=700, height=700)
        self.w.config(background='white')
        self.w.bind('<Button-1>', self.add_point)
        self.w.bind('<Motion>', self.mouse_position)
        self.w.pack()

        self.label_position = tk.Label(self.main_frame, text="Mouse Position: (0, 0)")
        self.label_position.pack(anchor="w")  

        self.frame_button = tk.Frame(self.master)
        self.frame_button.pack()
        
        self.draw_button = tk.Button(self.frame_button, text='Draw', width=25, command=self.draw)
        self.draw_button.pack(side=tk.LEFT)
        
        self.clear_button = tk.Button(self.frame_button, text='Clear', width=25, command=self.clear)
        self.clear_button.pack(side=tk.LEFT)

        self.text_input_button = tk.Button(self.frame_button, text="Input from File", width=25, command=self.read_input_from_file)
        self.text_input_button.pack(side=tk.LEFT)

    def mouse_position(self, event):
        """Display the current mouse position on the canvas."""
        self.label_position.config(text=f"Mouse Position: ({event.x}, {event.y})")

    def read_input_from_file(self):
        """Open a file explorer to choose a file and add points to the canvas."""
        if not self.LOCK_FLAG:
            file_path = fd.askopenfilename(
                title="Open Points File",
                filetypes=[("Text Files", "*.txt")]
            )

            if file_path:
                try:
                    with open(file_path, "r") as file:
                        for line in file:
                            line = line.strip()
                            if line:
                                x, y = map(float, line.split())
                                self.w.create_oval(
                                    x - self.RADIUS, y - self.RADIUS,
                                    x + self.RADIUS, y + self.RADIUS,
                                    fill=self.POINT_COLOR
                                )
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to read file: {e}")

    def draw(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
        
            # Get the list of Point objects that were clicked

            point_object = self.w.find_all()
            points = []
            for p in point_object:
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS))

            sites = []
            points_list = []

            print("Sites:")
            for site in points:
                print(f"({site[0]}, {site[1]})")
                points_list.append((site[0], site[1]))
                sites.append(Point(site[0], site[1]))

            # Create Voronoi diagram

            vp = Voronoi(sites)
            vp.compute()

            # Draw Voronoi edges (lines)

            lines = vp.get_output()
            self.draw_lines(lines)

            # Get and draw the largest circle(s) from the Voronoi diagram

            circles = vp.largest_circle(points)
            self.draw_largest_circle(circles)


    def clear(self):
        self.LOCK_FLAG = False
        self.w.delete(tk.ALL)

    def add_point(self, event):
        """Add a point on canvas if not locked."""
        if not self.LOCK_FLAG:
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill=self.POINT_COLOR)

    def draw_lines(self, lines):
        """Draw the Voronoi lines."""
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill=self.LINE_COLOR)

    def draw_largest_circle(self, circles):
        """
        Draw the largest circle(s) on the canvas.
        """
        for center, radius in circles:
            x, y = center.x, center.y
            self.w.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                outline=self.CIRCLE_COLOR, width=2
            )

def main(): 
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
