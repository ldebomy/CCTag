# -*- coding: utf-8 -*-
import json, os, math
import svgwrite
import argparse

# unit is mm

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate grids of markers for turntable')
    parser.add_argument('--pattern', metavar='file', type=str, default='./turntable.txt',
                        help='the pattern file for markers, default: %(default)s)')
    parser.add_argument('--xstep', metavar='N', type=float, default=40,
                        help='distance in mm between columns, default: %(default)s)')                        
    parser.add_argument('--ystep', metavar='N', type=float, default=40,
                        help='distance in mm between rows, default: %(default)s)') 
    parser.add_argument('--firstId', metavar='N', type=int, default=0,
                        help='first marker id, default: %(default)s)') 
    parser.add_argument('--markerRings', metavar='N', type=int, default=3, choices=[3, 4],
                        help='the number of rings (possible values {%(choices)s}, default: %(default)s)')
    parser.add_argument('--turntableRadius', metavar='N', type=int, default=160,
                        help='the radius in mm of the turntable (default: %(default)s)')
    parser.add_argument('--markerRadius', metavar='N', type=int, default=10,
                        help='the radius in mm of the outer circle of markers (default: %(default)s)')
    parser.add_argument('--fontSize', metavar='N', type=int, default=6,
                        help='font size of ids labels, 0 to disable')
    parser.add_argument('--crossSize', metavar='N', type=int, default=0,
                        help='add a small cross in the center of the marker of size cross_size or none if cross_size=0')    
    parser.add_argument('--outfileSvg', metavar='file', type=str, default='./turntable.svg',
                        help='the filename for svg (default: %(default)s)')
    parser.add_argument('--outfileJson', metavar='file', type=str, default='./turntable.json',
                        help='the filename for json (default: %(default)s)')
    args = parser.parse_args()

pattern = [ l.split(' ') for l in open(args.pattern, 'r').read().split('\n') ]
marker_size = 2 * args.markerRadius
marker_scale = args.markerRadius / 100.0
tag_file='cctag4.txt' if args.markerRings==4 else 'cctag3.txt'
markers_def = open(tag_file, 'r').read().split('\n')
x0=-args.xstep*((len(pattern[0])-1)/2.0)
y0=-args.ystep*((len(pattern)-1)/2.0)

markers = []
markerId=args.firstId

dwg = svgwrite.Drawing(args.outfileSvg, profile='tiny', size=(str(args.turntableRadius*2)+'mm', str(args.turntableRadius*2)+'mm'))

# turntable border with graduation
dwg.add(dwg.circle(center=(f'{args.turntableRadius}mm', f'{args.turntableRadius}mm'), r=f'{args.turntableRadius}mm', stroke='black', fill='white'))
for a in range(0, 360, 5):
    r=(a*math.pi)/180
    xc = math.cos(r)*args.turntableRadius
    yc = math.sin(r)*args.turntableRadius
    xf = math.cos(r)*(args.turntableRadius-5)
    yf = math.sin(r)*(args.turntableRadius-5)        
    sw='4mm' if a==0 else '1mm'
    s='red' if a==0 else 'black'
    dwg.add(dwg.line(start=(f'{args.turntableRadius+xc}mm', f'{args.turntableRadius+yc}mm'), end=(f'{args.turntableRadius+xf}mm', f'{args.turntableRadius+yf}mm'), stroke=s, stroke_width=sw))

y=y0
for row in pattern:
    x=x0
    for m in row:        
        if m=='*':            
            marker = { 
                "markerId" : markerId,
                "markerCoord" : ( x, 0, -y)
            }
            markers.append(marker)
            # DRAW MARKER
            line=markers_def[markerId]
            if args.fontSize>0:
                dwg.add(dwg.text(text=str(markerId), insert=(f'{args.turntableRadius+x-marker_size}mm', f'{args.turntableRadius+y+marker_size/2}mm'), font_size=f'{args.fontSize}mm'))        
            center=(args.turntableRadius+x, args.turntableRadius+y)
            # print the outer circle as black
            dwg.add(dwg.circle(center=(f'{center[0]}mm', f'{center[1]}mm'), r=f'{marker_size / 2}mm', fill='black'))
            fill_color = 'white'
            count = 0
            # each value of the line is the radius of the circle to draw
            # the values are given for a marker of radius 100 (so scale it accordingly to the given size)
            for r in line.split():
                radius = int(r)
                # print(r)
                dwg.add(dwg.circle(center=(f'{center[0]}mm', f'{center[1]}mm'), r=f'{marker_scale * radius}mm', fill=fill_color))
                if fill_color == 'white':
                    fill_color = 'black'
                else:
                    fill_color = 'white'
                count = count + 1
            # sanity check
            if args.markerRings == 3:
                assert count == 5
            else:
                assert count == 7
            #if args.addCross:
            ## print a small cross in the center
            if args.crossSize>0:
                dwg.add(dwg.line(start=(f'{center[0] - args.crossSize}mm', f'{center[1]}mm'), end=(f'{center[0] + args.crossSize}mm', f'{center[1]}mm'), stroke="gray"))
                dwg.add(dwg.line(start=(f"{center[0]}mm", f'{center[1] - args.crossSize}mm'), end=(f'{center[0]}mm', f'{center[1] + args.crossSize}mm'), stroke="gray"))
            markerId+=1            
        x+=args.xstep
    y+=args.ystep

dwg.save(pretty=True)
with open(args.outfileJson, 'w') as f:
    f.write(json.dumps(markers))