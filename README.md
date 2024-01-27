# lego-3d-scanner

A 3D small object scanner made (almost) entirely from LEGO parts. It scans the object by recording the height at each point in an x,y grid, using a force-sensitive probe that moves in the z direction.

## Parts & build

Uses parts from the LEGO [Spike Prime](https://education.lego.com/en-us/products/lego-education-spike-prime-set/45678), [Spike Prime Expansion](https://education.lego.com/en-us/products/lego-education-spike-prime-expansion-set/45681/), and [Large Creative Brick Box](https://www.lego.com/en-us/product/lego-large-creative-brick-box-10698?age-gate=grown_up), plus a lot of [rack gears](https://www.webrick.com/toothed-bar-m-1-z-10-3743.html)
for the x,y,z movement.
The one non-LEGO piece is the tip of a [spring bar tool](https://a.co/d/awqxNrj), used for the probe.

Specific Spike hardware used:

* 1 Spike Prime hub (the microcontroller)
* 1 large motor for the z axis
* 2 medium motors for the x,y axes
* 2 color sensors for calibrating x,y
* 1 force sensor for the z probe


The probe assembly moves in the x,y plane using motors on rack gears. The gear ratio is very low, allowing for precise positioning.

The probe itself moves in the z direction using a vertical rack gear. I use a metal [spring bar tool tip](https://a.co/d/awqxNrj) attached to a force sensor for the probe, allowing for precise measurements.

## Scanning

To do the scan, run `./scan.py` on the Spike hub using the [Spike app](https://education.lego.com/en-us/downloads/spike-app/software/).

Before scanning, position the probe to the most extreme x,y,z position.

The scanning program initializes by first setting the x, y, and z ranges, using the two color sensors and the force sensors to calibrate itself.

During scanning, the probe visits every point in an x,y grid, whose resolution is set in the code. At each x,y point, the scanner lowers the probe until the force sensor is triggered, transmits the x,y,z data to the computer, and resets the probe.

A full scan at the default resolution takes several hours, and the total distance traversed by the probe can be miles!

The scanning automatically stops if the gyro detects that the carriage has toppled over, or if the user requests an early stop by pressing an arrow button on the hub, or showing the x color sensor something red.

Once the program stops, you can export the CSV points data from the Spike app. I've provided some example scans in the [csv/](csv/) directory.

## Plotting

Once you have the CSV file, run `./plot.py FILE [OPTIONS]` from your terminal to view your 3D scan! It uses [PyVista](https://pyvista.org/#) for the 3D plotting.

You can navigate the camera by dragging the mouse and scrolling.

Run `./plot.py -h` for more view options.

Ex:

`./plot.py csv/knight10.csv --color beige`








