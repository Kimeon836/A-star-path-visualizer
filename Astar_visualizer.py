# For GUI
import tkinter as tk
# To delay time between blocks while visualizing
import time
# For handling arrays in more efficient manner
import numpy as np


# Node for each block containing values to help calculate the shortest path
class Node:
    def __init__(self, parent=None, position=None):
        # The Node's it's adjacent to
        self.parent = parent
        # It's position, (row, column)
        self.position = position

        # g, f, h values as per algorithm
        self.g = 0
        self.f = 0
        self.h = 0

    # Overwriting equivalent operator for this class
    def __eq__(self, other):
        return self.position == other.position


# Class App contains the main GUI and also the algorithm
class App:
    def __init__(self, canvas_height=800, canvas_width=800, side_length=16):
        self.root = tk.Tk()  # The master window of GUI
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.start_point = self.end_point = None
        self.rows = self.canvas_height // side_length
        self.cols = self.canvas_width // side_length
        # The first row and first column are obstacles by default for this App
        self.maze = np.array(
            [[1] + [1] * (self.cols - 1)] + [[1] + [0] * (self.cols - 1) for _ in range(self.rows - 1)])
        self.visStarted = False  # To make sure no changes occur while algorithm is running

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height,
                                bg="white")  # The canvas for all blocks
        self.side_length = side_length  # Side length of square block
        self.grid()

    # This function initializes the GUI and packs all widgets and buttons
    def start(self):
        self.root.title('A* Algorithm Path Visualiser')
        self.root.geometry(f"{self.canvas_height}x{self.canvas_width + 100}")

        self.text_box = tk.Label(self.root, text="Select starting point")
        self.text_box.config(font=("Courier", 14), bg="white")
        self.text_box.pack(side=tk.TOP, anchor=tk.CENTER)

        self.allow_diagonal_mov = tk.IntVar()
        self.allow_diagonal_mov.set(0)
        dchkbtn = tk.Checkbutton(self.root, text="Allow Diagonal Movement", variable=self.allow_diagonal_mov)
        dchkbtn.place(x=self.canvas_height * 0.1, y=25)

        self.delaytime = tk.DoubleVar()
        self.delaytime.set(0.06)  # Changing this value and offvalue below will affect animation speed
        tchkbtn = tk.Checkbutton(self.root, text="Show Solution Instantly", variable=self.delaytime, onvalue=0,
                                 offvalue=0.06)
        tchkbtn.place(x=self.canvas_height * 0.6, y=25)

        sbtn = tk.Button(self.root, text="Start", command=self.find_path)
        sbtn.place(x=self.canvas_height * 0.40, y=self.canvas_width + 70, anchor=tk.CENTER)

        rbtn = tk.Button(self.root, text="Reset all", command=self.reset)
        rbtn.place(x=self.canvas_height * 0.60, y=self.canvas_width + 70, anchor=tk.CENTER)

        self.canvas.place(x=0, y=50)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<Button-1>', self.draw)
        self.canvas.bind('<Button-3>', self.reset_block)
        self.canvas.bind('<Button3-Motion>', self.reset_block)
        self.root.bind("<space>", self.find_path)
        self.root.mainloop()

    # This function is called when 'Reset All' button is clicked. It resets the canvas and required variables
    def reset(self):
        self.visStarted = False
        self.maze = np.array(
            [[1] + [1] * (self.cols - 1)] + [[1] + [0] * (self.cols - 1) for _ in range(self.rows - 1)])
        self.canvas.delete("all")
        self.grid()
        self.start_point = self.end_point = None
        self.show_text("Select starting point")

    # This function is called when 'Start' button is clicked or <space> bar is pressed.
    # It checks if start and end point are initialized and then calls the 'Astar' function which is the main algorithm.
    def find_path(self, event=None):
        if self.start_point and self.end_point:
            self.Astar()
        elif self.start_point:
            self.show_text("Select destination point", "red")
        else:
            self.show_text("Select starting point", "red")

    # It's to change the text in instruction box to help user with running GUI
    def show_text(self, text, text_color="black"):
        self.text_box.config(text=text, fg=text_color)

    # It's to change the text in instruction box to help user with running GUI
    def show_block_text(self):
        if not self.start_point:
            self.show_text("Select starting point")
        elif not self.end_point:
            self.show_text("Select destination point")
        else:
            self.show_text("Make obstacles or Right click on any block to remove it.")

    # It's to get the position of block in terms of row and column depending upon the canvas co-ordinates
    def get_pos(self, side_length, coordinates):
        for i in range(1, self.rows):
            for j in range(1, self.cols):
                if coordinates[0] // side_length <= i and coordinates[1] // side_length <= j:
                    return (i, j)
        return None

    # It draws the grid and black blocks at boundary
    def grid(self):
        pad = self.side_length // 2

        self.canvas.create_rectangle(-pad, -pad, pad, pad, fill="black", outline="grey")

        for i in range(pad, self.canvas_height, self.side_length):
            self.canvas.create_line([(i, 0), (i, self.canvas_width)], tag='grid_line', fill="grey")
            self.canvas.create_rectangle(i, -pad, i + self.side_length, pad, fill="black", outline="grey")
            self.canvas.create_rectangle(-pad, i, pad, i + self.side_length, fill="black", outline="grey")

        new_pad = self.canvas_height - ((self.canvas_height // self.side_length) * self.side_length - pad)
        for i in range(pad, self.canvas_width, self.side_length):
            self.canvas.create_line([(0, i), (self.canvas_height, i)], tag='grid_line', fill="grey")
            self.canvas.create_rectangle(self.canvas_height - new_pad, i, self.canvas_height, i + self.side_length,
                                         fill="black", outline="grey")
            self.canvas.create_rectangle(i, self.canvas_height - new_pad, i + self.side_length, self.canvas_height,
                                         fill="black", outline="grey")

    # Function to draw square at given row and column
    def draw_sqaure(self, xa, ya, color):
        x, y = xa * self.side_length, ya * self.side_length
        x1, y1 = (x - self.side_length / 2), (y - self.side_length / 2)
        x2, y2 = (x + self.side_length / 2), (y + self.side_length / 2)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="grey")

    # This function is called when algorithm finds a path.
    # It retraces the path by following the Node's parent and so on till it reaches start point.
    def draw_path(self, current_node):
        self.show_text("Path Found!", "green")
        self.visStarted = False
        path = []
        while current_node is not None:
            self.draw_sqaure(current_node.position[0], current_node.position[1], "green")
            time.sleep(0.05)
            self.canvas.update()
            path.append(current_node.position)
            current_node = current_node.parent

        self.show_text(f"Path Found! Number of blocks required to reach destination is {len(path)}", "green")

    # This function is for drawing square blocks on user command.
    # It's called when Left Mouse button is clicked.
    def draw(self, event):
        if self.visStarted == True:
            return

        pos = self.get_pos(self.side_length, (event.x, event.y))

        if pos == None:
            return
        else:
            xa, ya = pos

        # It is to check which color of block should be drawn if start is None or end is None or if start and end
        # points overlap.
        if not self.start_point:
            self.start_point = Node(None, (xa, ya))
            color = "orange"
            if self.end_point:
                if self.start_point.position == self.end_point.position:
                    self.end_point = None

        elif self.start_point.position == (xa, ya):
            self.start_point = None

            if not self.end_point:
                self.end_point = Node(None, (xa, ya))
                color = "cyan"
            else:
                color = "black"

        elif not self.end_point:
            self.end_point = Node(None, (xa, ya))
            color = "cyan"

        elif self.end_point.position == (xa, ya):
            self.end_point = None

            if not self.start_point:
                self.start_point = Node(None, (xa, ya))
                color = "orange"
            else:
                color = "black"
        else:
            self.maze[xa][ya] = 1
            color = "black"

        self.draw_sqaure(xa, ya, color)
        self.show_block_text()

    # It resets the selected block.
    def reset_block(self, event=None):
        if self.visStarted == True:
            return

        pos = self.get_pos(self.side_length, (event.x, event.y))
        if pos == None:
            return
        else:
            xa, ya = pos

        if self.start_point:
            if self.start_point.position == (xa, ya):
                self.start_point = None
        if self.end_point:
            if self.end_point.position == (xa, ya):
                self.end_point = None

        self.maze[xa][ya] = 0

        self.draw_sqaure(xa, ya, "white")
        self.show_block_text()

    # It's the algorithm function which handles all operations for finding path.
    def Astar(self):
        self.show_text("A* Algorithm running")
        self.visStarted = True

        to_visit = np.array([])  # Nodes yet to be visited
        visited = np.array([])  # Nodes which are visited
        to_visit = np.append(to_visit, [self.start_point]) # Starting point is appended in to_visit

        # Checks if diagonal movement is allowed and changes allowed adjacent cells range accordingly.
        if self.allow_diagonal_mov.get():
            adj_cells = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        else:
            adj_cells = [(0, 1), (1, 0), (-1, 0), (0, -1)]

        counter = 0
        max_count = (len(self.maze) // 2) ** 10 # A reasonable amount of max iterations.

        # loop will be run until there are nodes to visit or until path is found
        while to_visit.size > 0:
            # If reset all button is clicked then it will immediately stop the algorithm
            if not self.visStarted:
                return
            counter += 1  # Keeping track of number of iterations

            time.sleep(self.delaytime.get()) # Delay to visualize in smooth manner
            self.canvas.update()

            current_node = to_visit[0]

            idx = 0
            for index, item in enumerate(to_visit):
                # If another nodes f value is lesser then it is prioritized.
                if item.f < current_node.f:
                    current_node = item
                    idx = index

            # Break loop if limit exceeds
            if counter > max_count:
                break

            # Deleting current node from to_visit array and adding it to visited one
            to_visit = np.delete(to_visit, idx)
            self.draw_sqaure(current_node.position[0], current_node.position[1], "red")
            visited = np.append(visited, [current_node])

            # If current node is end point then we have found the shortest path
            if current_node == self.end_point:
                return self.draw_path(current_node)

            # Children is array containing adjacent cell of current node
            children = np.array([])
            for new_position in adj_cells:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                # To make sure it is within range of length of rows and columns
                if node_position[0] > (len(self.maze) - 1) or node_position[0] < 0 or node_position[1] > (
                        len(self.maze[len(self.maze) - 1]) - 1) or node_position[1] < 0:
                    continue

                # To check if it's an obstacle or not. Obstacle has value 1
                if self.maze[node_position[0]][node_position[1]] != 0:
                    continue

                # Instance of Node Class is made with parent being current node and it's then appended to children array.
                new_node = Node(current_node, node_position)
                children = np.append(children, [new_node])

            # This loop calculates the f, g and h and checks if these nodes are previously visited.
            for child in children:
                # To check if it has been visited before
                if len([i for i in visited if child == i]) > 0:
                    continue

                # Here, cost of all edges is 1
                child.g = current_node.g + 1
                child.h = ((child.position[0] - self.end_point.position[0]) ** 2 +
                           (child.position[1] - self.end_point.position[1]) ** 2)
                child.f = child.g + child.h

                if len([j for j in to_visit if child == j and child.g > j.g]) > 0:
                    continue

                self.draw_sqaure(child.position[0], child.position[1], "yellow")
                to_visit = np.append(to_visit, [child])  # It is then added to_visit array so we can check it's adjacent cell and so forth.
        self.show_text("Wouldn't find path", "red")
        self.visStarted = False

# Here, you can set canvas height, canvas width and side length of block
def main():
    app = App(800, 800, 16)
    app.start()


if __name__ == '__main__':
    main()
