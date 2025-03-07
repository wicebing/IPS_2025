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


indoorPosition <- read.csv("C:/Users/USER/Downloads/IPS/areaPct_exp1_15hr.csv")
data_all <- indoorPosition

#data_all$ev <- with(data_all, event==2 | event==1)
#data_all_c <- subset(data_all , event==0 | event==1)
#data_all_f <- subset(data_all , event==0 | event==2)
data_all <- within(data_all, {
  event_c <- as.factor(event_c)
})

data_all <- within(data_all, {
  event_f <- as.factor(event_f)
})

t.test(cover_area_pct~event_c, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)
t.test(cover_area_pct~event_f, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)
