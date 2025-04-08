library("writexl")
library(openxlsx)
library(readxl)
library(mgcv)
library(oddsratio)
library('vcd')
library(postHoc)

library(foreign)
library(ggplot2)
library(MASS)
require(boot)


indoorPosition <- read.csv("C:/Users/USER/Downloads/IPS/lossTick_byHourBeacon.csv")
data_all <- indoorPosition

numSummary(indoorPosition[,"distance_to_route", drop=FALSE], 
           statistics=c("mean", "sd", "IQR", "quantiles"), quantiles=c(0,.25,.5,.75,1))

with(indoorPosition, (t.test(distance_to_route, alternative='two.sided', 
                             mu=0.0, conf.level=.95)))

cdf = ecdf(data_all$distance_to_route)
curve(cdf,xlim = c(0,1.62))
abline(h=0.8,lty=3)
abline(v=0.554243,lty=4)


# > numSummary(indoorPosition[,"distance_to_route", drop=FALSE], 
# +            statistics=c("mean", "sd", "IQR", "quantiles"), quantiles=c(0,.25,.5,.75,1))
# mean        sd       IQR            0%       25%       50%       70%       75%      80%     100%   n
# 0.3456778 0.2815841 0.3868638 0.00007230183 0.1283084 0.2801197 0.4581863 0.5151722 0.554243 1.613921 419
#      100%   n
#  1.613921 419
# > with(indoorPosition, (t.test(distance_to_route, alternative='two.sided', 
# +                              mu=0.0, conf.level=.95)))

# 	One Sample t-test

# data:  distance_to_route
# t = 25.129, df = 418, p-value < 2.2e-16
# alternative hypothesis: true mean is not equal to 0
# 95 percent confidence interval:
#  0.3186377 0.3727179
# sample estimates:
# mean of x 
# 0.3456778 