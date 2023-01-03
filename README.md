# salary-transparency
 
## Flask App
https://ishengy.pythonanywhere.com/ 
 
## Distribution Parameters
If the Flask App stops working for one reason or another, you can find the parameters to develop the distributions yourself in the [/src/data](https://github.com/ishengy/salary-transparency/blob/main/src/data/job_dist_parameters.csv) folder

## Abstract

Since November 1st 2022, NYC law mandates that salary bands are included in the job description. This makes New York City one of a handful of locations that provide this information even before the interview stage. In an attempt to make this data even more easily accessible to people out looking for a new job or negotiating a raise, I created this repo to house a few classes that will gather job descriptions from LinkedIn for specific job titles, extract the salary band information, develop a distribution, and even attempt to rescale that data to another location based on cost of living adjustments indicies with NYC as its baseline.

It's not a perfect solution but I hope this information will provide some benefit for someone out there.

