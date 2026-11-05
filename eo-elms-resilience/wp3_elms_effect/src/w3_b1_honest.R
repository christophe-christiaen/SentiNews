# W3-B1 section 2 (protocol: w3_b1_inference_protocol.md): Rambachan and Roth (2023), relative magnitudes, on the event studies
# of the hazard contrast. Input results/w3_b1_events.json; output results/w3_b1_honest.json (aggregates only).
args <- commandArgs(trailingOnly = TRUE)
res <- args[1]
options(warn = 1)
library(HonestDiD); library(jsonlite)
ev <- fromJSON(file.path(res, "w3_b1_events.json"), simplifyVector = TRUE)
grid <- seq(0, 2, by = 0.25)
out <- list()
for (nm in names(ev)) {
  x <- ev[[nm]]
  beta <- as.numeric(x$beta); V <- matrix(as.numeric(x$V), length(beta), length(beta), byrow = TRUE)
  stopifnot(length(beta) == 7, isSymmetric(V, tol = 1e-8))
  for (tg in c("average", "first")) {
    l <- if (tg == "average") rep(1 / 4, 4) else c(1, 0, 0, 0)
    orig <- constructOriginalCS(betahat = beta, sigma = V, numPrePeriods = 3, numPostPeriods = 4, l_vec = l)
    rob <- createSensitivityResults_relativeMagnitudes(betahat = beta, sigma = V, numPrePeriods = 3, numPostPeriods = 4,
                                                       Mbarvec = grid, l_vec = l)
    rob <- as.data.frame(rob)
    inc <- rob$lb <= 0 & rob$ub >= 0
    out[[length(out) + 1]] <- list(target = nm, parameter = tg, estimate = sum(l * beta[4:7]), original_lb = orig$lb, original_ub = orig$ub,
                                   pre = beta[1:3], sets = rob[, c("Mbar", "lb", "ub")],
                                   breakdown_Mbar = if (any(inc)) min(rob$Mbar[inc]) else NA,
                                   breakdown_note = if (any(inc)) "smallest grid value whose set includes zero" else "above the grid")
    message(nm, " ", tg, " breakdown ", if (any(inc)) min(rob$Mbar[inc]) else NA)
  }
}
write_json(out, file.path(res, "w3_b1_honest.json"), auto_unbox = TRUE, digits = 8, pretty = TRUE)
