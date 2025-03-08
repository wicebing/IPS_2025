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


indoorPosition <- read.csv("C:/Users/USER/Downloads/IPS/areaPct_exp1_30hr.csv")
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

indoorPosition <- within(indoorPosition, {
  hour <- as.factor(hour)
})
indoorPosition <- within(indoorPosition, {
  weekday <- as.factor(weekday)
})

t.test(cover_area_pct~event_c, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)
t.test(cover_area_pct~event_f, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)

GLM.2 <- glm(event_f ~ cover_area_pct + hour + weekday, 
             family=binomial(logit), data=indoorPosition)
summary(GLM.2)
exp(coef(GLM.2))  # Exponentiated coefficients ("odds ratios")

GLM.3 <- glm(event_c ~ cover_area_pct + hour + weekday, 
             family=binomial(logit), data=indoorPosition)
summary(GLM.3)
exp(coef(GLM.3))  # Exponentiated coefficients ("odds ratios") 看分布面積對事件的影響

GLM.4 <- glm(cover_area_pct ~ event_c + hour + weekday, 
             family=binomial(logit), data=indoorPosition)
summary(GLM.4)
exp(coef(GLM.4))  # Exponentiated coefficients ("odds ratios") 看事件對分布面積的影響
