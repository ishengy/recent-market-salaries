# salary-transparency
 
## Abstract

Since November 1st 2022, NYC law mandates that salary bands are included in the job description. This makes New York City one of a handful of locations that provide this information even before the interview stage. In an attempt to make this data even more easily accessible to people out looking for a new job or negotiating a raise, I created this repo to house a few classes that will gather job descriptions from LinkedIn for specific job titles, extract the salary band information, develop a distribution, and even attempt to rescale that data to another location based on cost of living adjustments indicies with NYC as its baseline.

It's not a perfect solution but I hope this information will provide some benefit for someone out there.

## Caveat(s)

It's slow. I'm averaging 2.5s per job description, which gets even worse if you're pulling hundreds of jobs. This is unfortunately the result of a disappoint lack of job search API documentation from both LinkedIn and Indeed. As passionate as I am about this project, it's not enough for me to spend that much more time looking for updated documentation and build the python wrapper myself. Thus, this project inherits from an existing package.

## Getting Started

## Google Sheets Information
