CATSPF = Common Assembly Test Second Part Fast

CATFP = Common Assembly Test First Part

CATSPFGrapher_1D_Histograms can make single plot, 1D histograms of IVCurve, Disconnected Bumps, and Noise Threshold tests which are useful for presenting in assembly meetings

CATSPFGrapher_Detailed makes single and multi plot, 2D histograms of IVCurve, Disconnected Bumps, and Noise Threshold tests which are useful for identifying specific module deficiencies

How to use the Code:

1. Navigate to the desired graphing script

2. Make sure the correct file paths are specified at the top of the script + have the most recent json downloaded from Panthera

3. Make sure all the modules you want to plot are in the MODULE_NAMES vector (only TFPX 1x2 (RH) and 2x2 (SH) modules work for now)

4. Run the code using the play button at the top right

5. The terminal will tell you if any modules you entered are missing from the JSON file and ask if you want to terminate the code or continue

6. The terminal will prompt you to enter a number corresponding to which test you want to plot

7. The terminal will prompt you to enter a number corresponding to which treshold for that test you want to plot

8. The code will generate a graph into a subfolder in the PantheraPlots folder with the current day's date

NOTE: As of right now, if you generate a plot for the same test on the same day it will save over the existing png of that test made on that day because they have the same file name. To avoid this, rename tests as you see fit or make another folder to move existing tests to before plotting again.
