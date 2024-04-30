# Texas Hold'em Coevolution

## Introduction

This project applies competitive coevolution to poker, and explores the suitability of different methods and techniques. This was designed for my undergraduate dissertation at the University of York ('An Investigation of Co-evolutionary Dynamics Using Six-Handed Texas Hold’em Poker').

## Structure & Usage

`ParetoSixPlayerPoker.py` implements the poker game that can be used with pareto (and non-pareto) evolution methods.

There are six main python files that evolve strategy. Each one matches to a method as defined in the project writeup.

The 'Gathering Results' folder contains all the data used in the project, and the file 'CIAOplots.py'. This file can be used to generate the CIAO plots, fitness graphs and elite bitmaps that were used in the results section of the project.

You must specify the folder locations to generate data yourself with `pickle.load()`

