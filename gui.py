import tkinter as tk

from voronoi import Voronoi
from voronoi import Point
from voronoi import largest_circle

class MainWindow:
    # radius of drawn points on canvas
    RADIUS = 3

    # flag to lock the canvas when drawn
    LOCK_FLAG = False
    
    def __init__(self, master):
        self.master = master
        self.master.title("Voronoi")

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=500, height=500)
        self.w.config(background='white')
        self.w.bind('<Double-1>', self.onDoubleClick)
        self.w.bind('<Motion>', self.showMousePosition)  # Bind mouse motion event
        self.w.pack()

        self.lblPosition = tk.Label(self.frmMain, text="Mouse Position: (0, 0)")
        self.lblPosition.pack(anchor="w")  # Align to the left side

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()
        
        self.btnCalculate = tk.Button(self.frmButton, text='Calculate', width=25, command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)
        
        self.btnClear = tk.Button(self.frmButton, text='Clear', width=25, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)

    def showMousePosition(self, event):
        """Display the current mouse position on the canvas."""
        self.lblPosition.config(text=f"Mouse Position: ({event.x}, {event.y})")
        
    def onClickCalculate(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
        
            pObj = self.w.find_all()
            points = []
            for p in pObj:
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS))

            sites = []
            points_list = []

            print("Sites:")
            for site in points:
                print(f"({site[0]}, {site[1]})")
                points_list.append((site[0], site[1]))
                sites.append(Point(site[0], site[1]))

            vp = Voronoi(sites)

            vp.compute()
            lines = vp.get_output()
            self.drawLinesOnCanvas(lines)

            vertices = vp.print_vertices()
            print("Vertices: ",vertices)

            circle = largest_circle(points, vertices)
            print(circle)
            self.drawLargestCircle(circle)


    def onClickClear(self):
        self.LOCK_FLAG = False
        self.w.delete(tk.ALL)

    def onDoubleClick(self, event):
        if not self.LOCK_FLAG:
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill="black")

    def drawLinesOnCanvas(self, lines):
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill='blue')

    def drawLargestCircle(self, circles):
        """
        Draw the largest circle(s) on the canvas.
        :param circles: List of tuples [(center_x, center_y, radius), ...] representing the circles.
        """
        for center, radius in circles:
            x, y = center
            self.w.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                outline="green", width=2
            )

def main(): 
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
