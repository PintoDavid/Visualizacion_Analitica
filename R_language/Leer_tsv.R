# Instala el paquete si no lo tienes
if (!requireNamespace("readr", quietly = TRUE)) {
  install.packages("readr")
}
if (!requireNamespace("utils", quietly = TRUE)) {
  install.packages("utils")
}

library(readr)
library(utils)

# Función para detectar el separador correcto
detect_separator_tsv <- function(file_path, separators = c("\t", ",", ";", " ", "|")) {
  separator_results <- data.frame(Separator = character(), Columns = integer(), stringsAsFactors = FALSE)
  
  for (sep in separators) {
    # Intentamos leer las primeras líneas del archivo con cada separador
    temp_data <- tryCatch({
      read_delim(file_path, delim = sep, n_max = 5, show_col_types = FALSE)
    }, error = function(e) {
      NULL
    })
    
    # Si se ha leído correctamente, guardamos el número de columnas detectado
    if (!is.null(temp_data)) {
      separator_results <- rbind(separator_results, data.frame(Separator = sep, Columns = ncol(temp_data)))
    }
  }
  
  return(separator_results)
}

# Seleccionar archivo TSV mediante una ventana emergente
file_path <- file.choose()

# Detectar separadores posibles (incluyendo tabulador como opción principal)
separator_results <- detect_separator_tsv(file_path)

# Mostrar los separadores probados y el número de columnas detectadas para cada uno
print(separator_results)

# Seleccionar el separador más probable (el que tenga más columnas consistentes)
best_separator <- separator_results$Separator[which.max(separator_results$Columns)]

# Leer el archivo completo con el mejor separador detectado
data <- read_delim(file_path, delim = best_separator)

# Mostrar las primeras filas del dataframe cargado
head(data)

