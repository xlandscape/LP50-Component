library(data.table)
library(drc)

input_file <- commandArgs(TRUE)[1]
output_file <- commandArgs(TRUE)[2]

data <- fread(input_file)
slices <- data[, .N, .(year, reach)]
result <- rbindlist(lapply(1:slices[, .N], function(i) {
  y <- slices[i, year]
  rch <- slices[i, reach]
  x <- data[year == y & reach == rch]
  if (x[value < .01, .N] == x[, .N]) {
    data.table(
      year = y,
      reach = rch,
      estimate = -997,
      std.error = -997,
      upper = -997,
      lower = -997,
      result = "NO CONVERGENCE - ALL VALUES <.01"
    )
  } else if (x[value > .99, .N] == x[, .N]) {
    data.table(
      year = y,
      reach = rch,
      estimate = -998,
      std.error = -998,
      upper = -998,
      lower = -998,
      result = "NO CONVERGENCE - ALL VALUES >.99"
    )
  } else {
    m <- tryCatch(drm(x[, value] ~ x[, factor], fct = LL.2(), control = drmc(errorm = FALSE)), error = function() { })
    if (is(m, "drc")) {
      lp50 <- ED(m, 50, interval = "tfls")
      data.table(
        year = y,
        reach = rch,
        estimate = lp50[1],
        std.error = lp50[2],
        upper = lp50[3],
        lower = lp50[4],
        result = "FIT"
      )
    } else {
      data.table(year = y, reach = rch, estimate = -999, std.error = -999, upper = -999, lower = -999, result = "ERROR")
    }
  }
}))
fwrite(result, output_file)
