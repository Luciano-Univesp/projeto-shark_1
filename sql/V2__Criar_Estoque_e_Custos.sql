CREATE TABLE IF NOT EXISTS `insumos` (
  `idinsumos` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `unidade_medida` VARCHAR(100) NOT NULL,
  `quantidade_estoque` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`idinsumos`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `custos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `custos` (
  `id_custos` INT NOT NULL AUTO_INCREMENT,
  `descricao` VARCHAR(100) NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL,
  `data_custo` DATE NULL,
  PRIMARY KEY (`id_custos`))
ENGINE = InnoDB;
