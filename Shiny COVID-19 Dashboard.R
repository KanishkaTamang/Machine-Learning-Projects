library(shinydashboard)
library(shiny)
library(readxl)
library(readr)
library(ggplot2)
library(leaflet)
library(dplyr)
library(plotly)
library(lubridate)
library(rsconnect)
#Reading the datasets
cases <- read_excel("cases_official.xlsx")
cases <- cases[complete.cases(cases$lhd_2010_name), ]
cases$month_date <- month.name[month(cases$notification_date)]
cases$month_date <- factor(cases$month_date, levels = month.name)
cases_map <- read_excel("tanara.xlsx")
cases_age <- read_csv("covid-19-cases-by-notification-date-and-age-range.csv")
cases_age$month_date <- month.name[month(cases_age$notification_date)]
cases_age$month_date <- factor(cases_age$month_date, levels = month.name)
test <- read_excel("total_test.xlsx")
test$month_date <- month.name[month(test$test_date)]
test$month_date <- factor(test$month_date, levels = month.name)
# Define UI for application that draws a histogram
ui <- dashboardPage(
  dashboardHeader(title = "COVID-19 NSW"),
  dashboardSidebar(
    menuItem("Select LHD:", tabName = "cases", icon = icon("calendar"),
             selectInput("select_lhd", " ",
                         choices = unique(cases$lhd_2010_name)),
             helpText("The Government of New South Wales (Data Analytics Centre) has published datasets
on COVID-19 highlighting total confirmed cases, sources of infection and tests conducted in each Local
Health District of NSW."),
             helpText(a("Click here-Data Source:(NSW
Government,2020)",href="https://data.nsw.gov.au/nsw-covid-19-data"))
    )),
  dashboardBody(
    fluidRow(
      box(width = 6, title = "Total Confirmed Cases From January To May, 2020", status = "primary",
          solidHeader = TRUE,
          collapsible = TRUE,
          leafletOutput("map")),
      box(width = 6, title = "Total number of Covid-19 tests", status = "primary", solidHeader = TRUE,
          collapsible = TRUE,
          plotlyOutput("test"))
    ),
    fluidRow(
      box(width = 6, title = "Total number of Covid-19 confirmed cases",status = "primary", solidHeader =
            TRUE,
          collapsible = TRUE,
          plotlyOutput("plot1")),
      box(width = 6, title = "Sources of COVID-19", status = "primary", solidHeader = TRUE,
          collapsible = TRUE,
          plotlyOutput("plot2", height = '400px'))
    )
  )
)
# Define server logic required to draw a histogram
server <- function(input, output, session) {
  output$plot1 <- renderPlotly({
    case_filter <- cases[cases$lhd_2010_name ==input$select_lhd,]
    cases_by_month <- case_filter %>% dplyr::group_by(lhd_2010_name, month_date) %>% count(result)
    cases_by_month <- cases_by_month[complete.cases(cases_by_month$lhd_2010_name), ]
    graph_title <- paste("Number of Covid-19 cases in", input$select_lhd)
    p <- ggplot(cases_by_month, aes(x = month_date, y = n, fill = lhd_2010_name)) +
      geom_bar(stat="identity", position = "dodge") +
      scale_x_discrete(" ") + theme(plot.title = element_text(hjust = 0.5, size = 11, face = "bold"),
                                    legend.position = "none") + theme(plot.title = element_text(size = 11, face = "bold")) +
      geom_text(aes(label= n), vjust=1.6, color="black", size=4, position = position_dodge(0.9)) + labs(title
                                                                                                        = graph_title, y ="Count", fill = "Legend Title\n")
  })
  output$plot2 <- renderPlotly({
    case_filter <- cases[cases$lhd_2010_name ==input$select_lhd,]
    cases_by_infection <- case_filter %>% group_by(lhd_2010_name, month_date) %>%
      count(likely_source_of_infection)
    cases_by_infection <- cases_by_infection[complete.cases(cases_by_infection$lhd_2010_name), ]
    graph_title_2 <- paste("Sources of Covid-19 infection in", input$select_lhd)
    p2 <- ggplot(cases_by_infection, aes(x = month_date, y = n, fill = likely_source_of_infection))
    +geom_bar(stat="identity", position = "dodge") +
      scale_x_discrete(" ") + labs(title = graph_title_2, y ="Count", fill = "Legend Title\n") +
      theme(legend.text=element_text(size=8.5)) +theme(plot.title = element_text(hjust = 0.5, size = 10, face
                                                                                 = "bold")) +
      geom_text(aes(label= n), vjust=1.6, color="black", size=2.5, position = position_dodge(0.9))
    ggplotly(p2) %>%
      layout(legend = list(orientation = "h", x= 0.9, y = -0.1))
  })
  output$map <- renderLeaflet({
    pal <- colorNumeric(
      palette = "RdYlBu",
      domain = cases_map$n)
    mapplot <- leaflet()%>%
      addTiles() %>%
      addCircles(data = cases_map,
                 lng = ~lon, lat = ~lat,
                 weight = 10,
                 radius = ~ n,
                 popup = paste("Postcode:", cases_map$postcode, "<br>",
                               "Count:", cases_map$n),
                 color = ~pal(n),
                 fillOpacity = 5
      ) %>% setView(lng = 145.612793, lat = -31.840233, zoom = 4.5) %>%
      addLegend(pal = pal, values =cases_map$n, group = cases_map$postcode, position = "bottomright",
                title = "Total Cases")
  })
  output$test <- renderPlotly({
    test_filter <- test[test$lhd_2010_name ==input$select_lhd,]
    test_by_month <- test_filter %>% dplyr::group_by(lhd_2010_name, month_date) %>%
      count(Total_Test)
    test_by_month <- test_by_month[complete.cases(test_by_month$lhd_2010_name), ]
    graph_title_3 <- paste("Number of Covid tests in", input$select_lhd)
    p <- ggplot(test_by_month, aes(x = month_date, y = n, fill = lhd_2010_name)) +
      geom_bar(stat="identity", position = "dodge") +
      scale_x_discrete(" ") + theme(plot.title = element_text(hjust = 0.5, size = 11, face = "bold"),
                                    legend.position = "none") + theme(plot.title = element_text(size = 11, face = "bold")) +
      geom_text(aes(label= n), vjust=1.6, color="black", size=4, position = position_dodge(0.9)) + labs(title =
                                                                                                          graph_title_3, y ="Count", fill = "Legend Title\n")
  })
}
# Run the application
shinyApp(ui = ui, server = server)