from pyautocad import *
from tkinter import *

class GUI:

    def __init__(self, window) -> None:
        self.l = 4
        self.window = window
        window.title('Октантное дерево')
        window.geometry('320x69')
        self.length_text = Label(window, text="Уровень разбиения", font=("Arial Bold", 14))
        self.length_text.grid(column=0, row=14)
        self.length_enter = Entry(window, width=10)
        self.length_enter.insert(END, '4')
        self.length_enter.grid(column=1, row=14)
        self.ok_button = Button(text='Ok', command=self.collectData, width=15)
        self.ok_button.grid(column=0, row=15)
        self.cancel_button = Button(text='Cancel', command=self.quit, width=15)
        self.cancel_button.grid(column=1, row=15)

    def quit(self):
        self.window.destroy()

    def collectData(self):
        self.l = float(self.length_enter.get())
        self.quit()

    def getData(self):
        return self.l


def main():
    print("Hi again :(")

    # opening CAD-file

    acad = Autocad(create_if_not_exists=True)
    print(acad.doc.name)
    print('|D| opening CAD-file')

    # get split level

    window = Tk()
    my_gui = GUI(window)
    window.mainloop()
    splitLevel = my_gui.getData()
    print('|D| get split level')

    # looking for polygon

    polyline = None
    for object in acad.iter_objects("Polyline"):
        polyline = object
    polyline.Color = 5
    polygon = list(polyline.Coordinates)
    if (len(polygon) % 2 != 0):
        print('|E| polygon\' length is incorrect')
    numberOfPoints = int(len(polygon) / 2 - 1)
    x = []
    y = []
    i = 0
    while i < numberOfPoints:
        x.append(polygon[2 * i])
        y.append(polygon[2 * i + 1])
        i += 1
    print('|D| looking for polygon')

    # finding root coordinates

    xmin = xmax = x[0]
    ymin = ymax = y[0]
    i = 1
    while i < numberOfPoints:
        if x[i] > xmax:
            xmax = x[i]
        if x[i] < xmin:
            xmin = x[i]
        if y[i] > ymax:
            ymax = y[i]
        if y[i] < ymin:
            ymin = y[i]
        i += 1
    if xmax - xmin > ymax - ymin:
        side = xmax - xmin
        ymax = ymin + side
    else:
        side = ymax-ymin
        xmax = xmin+side
    print('|D| finding root coordinates')

    # drawing octants

    rootoctant = [xmin, ymin, xmax, ymax]
    octant(acad, polyline, rootoctant, rootoctant, 0, splitLevel)

    print('|D| drawing octants')


def drawSquare(acad, x1, y1, x2, y2):
    acad.model.addLine(APoint(x1, y1), APoint(x1, y2))
    acad.model.addLine(APoint(x1, y2), APoint(x2, y2))
    acad.model.addLine(APoint(x2, y2), APoint(x2, y1))
    acad.model.addLine(APoint(x2, y1), APoint(x1, y1))


def octant(acad, polyline, curSquare, rootcoords, cursplit, reqsplit):
    color = whatcolor(acad, polyline, rootcoords, curSquare)
    if color == 3:
        drawSquare(acad, curSquare[0], curSquare[1], curSquare[2], curSquare[3])
    if color == 2:
        cursplit += 1
        if cursplit < reqsplit:
            side = (curSquare[2] - curSquare[0]) / 2
            octant(acad, polyline, [curSquare[0], curSquare[1], curSquare[0] + side, curSquare[1] + side], rootcoords, cursplit, reqsplit)
            octant(acad, polyline, [curSquare[0], curSquare[1] + side, curSquare[0] + side, curSquare[3]], rootcoords, cursplit, reqsplit)
            octant(acad, polyline, [curSquare[0] + side, curSquare[1] + side, curSquare[2], curSquare[3]], rootcoords, cursplit, reqsplit)
            octant(acad, polyline, [curSquare[0] + side, curSquare[1], curSquare[2], curSquare[1] + side], rootcoords, cursplit, reqsplit)
    return


def whatcolor(acad, polyline, rootcoords, square):  # 1 is White, 2 is Grey, 3 is Black

    # check if grey

    a = (square[2] - square[0]) / 2
    polysquare = tuple([square[0], square[1], 0.0, square[0], square[3], 0.0, square[2], square[3], 0.0, square[2], square[1], 0.0, square[0], square[1], 0.0])
    testline = acad.model.AddPolyLine(aDouble(polysquare))

    intersectpointsxyz = testline.IntersectWith(polyline, 0)
    numofpoints1 = int(len(intersectpointsxyz) / 3)
    testline.Delete()
    if numofpoints1 > 1:
        print("|D whatcolor| grey")
        return 2

    # check white or black

    testline = acad.model.addline(APoint(rootcoords[2], rootcoords[3]), APoint(square[0]+a, square[1]+a))
    numofpoints2 = int(len(testline.IntersectWith(polyline, 0))/3)
    testline.Delete()
    if numofpoints2 % 2 == 0:
        print("|D whatcolor| white")
        return 1
    else:
        print("|D whatcolor| black")
        return 3


if __name__ == '__main__':
    main()