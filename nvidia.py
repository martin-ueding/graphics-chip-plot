#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import colorsys
import itertools
import math
import pprint
import re

import matplotlib.pyplot as pl

pattern_chip = re.compile(r'^(NV.{2,3})[^\t]*\t(.*)$')

pattern_paren = re.compile(r'([^(]*)\(([^)]*)\)(.*)')

pattern_names = [
    [re.compile('GeForce [A-Z]+ (\d)0(\d0)'), 3],
    [re.compile('GeForce [A-Z]+ (\d)(\d\d)'), 2],
    [re.compile('GeForce (\d)(\d0)0 [A-Z]+'), 1],
]

def coloriter(n):
    return iter([
        colorsys.hsv_to_rgb(x*1.0/n, 1.0, .8)
        for x in range(n)
])

def expand_line(line):
    '''
    >>> expand_line('GeForce GT 630, 635, 640, 710M, 720M, 730M, 735M, 740M')
    ['GeForce GT 630', 'GeForce GT 635', 'GeForce GT 640', 'GeForce GT 710M', 'GeForce GT 720M', 'GeForce GT 730M', 'GeForce GT 735M', 'GeForce GT 740M']

    >>> expand_line('GeForce FX 5100 Go, 5200 (Ultra, Go), 5300, 5500, GeForce PCX 5300')
    ['GeForce FX 5100 Go', 'GeForce FX 5200 Ultra', 'GeForce FX 5200 Go', 'GeForce FX 5300', 'GeForce FX 5500', 'GeForce PCX 5300']
    '''
    if not line.startswith('GeForce'):
        return []

    top_parts = re.split(r',(?!(?:[^(]*\([^)]*\))*[^()]*\))', line)

    results = []

    for top_part in top_parts:
        top_part = top_part.strip()

        if not top_part.startswith('GeForce'):
            top_part = 'GeForce ' + top_part

        m = pattern_paren.match(top_part)
        if m:
            prefix, paren, suffix = m.groups()

            words = [x.strip() for x in paren.split(',')]
            if len(words) == 1:
                factors = ['', words[0]]
            else:
                factors = words

            for elem in factors:
                results.append(prefix + elem + suffix)
        else:
            results.append(top_part)

    return results


def get_unified_id(name):
    for pattern, epoch in pattern_names:
        m = pattern.search(name)
        if m:
            series, level = m.groups()

            return (int(epoch), int(series), int(level))

    print('ERROR', repr(name))



def main():
    options = _parse_args()

    pp = pprint.PrettyPrinter()

    with open('nvidia.txt') as f:
        lines = f.readlines()

    chips = {}

    for line in lines:
        card_lines = []
        m = pattern_chip.match(line.strip())
        if m:
            chip = m.group(1)
            chips[chip] = []
            chips[chip] += expand_line(m.group(2))
        else:
            chips[chip] + expand_line(line.strip())

    unified_pre = {
        chip: [x for x in [get_unified_id(name) for name in names] if x is not None]
        for chip, names in chips.items()
    }

    unified = {
        chip: names
        for chip, names in unified_pre.items()
        if len(names) > 0
    }

    #pp.pprint(chips)
    pp.pprint(unified)

#    for chip, lines in chips.items():
#        print()
#        print('Chip:\t', chip)
#        for line in lines:
#            print('Line:\t', line)
#            print('Expanded:\t', expand_line(line))


    color = coloriter(len(unified))

    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    i = 0
    for chip, points in sorted(unified.items()):
        if len(points) >= 1:
            x = [epoch * 10 + series for epoch, series, level in points]
            y = [level + i/40 for epoch, series, level in points]

            x, y = zip(*sorted(zip(x, y)))

            ax.plot(x, y, label=chip, marker='o', color=next(color), linestyle='none')
        i += 1

    ax.set_title('Usage of NVIDIA chips')
    ax.set_xlabel('Epoch * 10 + Series')
    ax.set_ylabel('Level digit')
    ax.margins(0.05)
    ax.grid(True)
    #pl.legend(loc='best', prop={'size': 5})
    fig.tight_layout()
    fig.savefig('plot-nvidia.pdf')

    sqrt = int(math.sqrt(len(unified)))
    rows = sqrt
    cols = sqrt
    while rows * cols < len(unified):
        cols += 1

    fig_grid = pl.figure(figsize=(20, 20))

    i = 0
    for chip, points in sorted(unified.items()):
        print(i)
        if len(points) >= 1:
            x = [epoch * 10 + series for epoch, series, level in points]
            y = [level for epoch, series, level in points]

            x, y = zip(*sorted(zip(x, y)))

            ax_grid = fig_grid.add_subplot(cols, rows, i + 1)
            ax_grid.plot(x, y, label=chip, marker='o', linestyle='none')
            ax_grid.set_xlim(ax.get_xlim())
            ax_grid.set_ylim(ax.get_ylim())
            ax_grid.grid(True)
            ax_grid.set_title(chip)
        i += 1

    fig_grid.tight_layout()
    fig_grid.savefig('plot-grid.pdf')


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
