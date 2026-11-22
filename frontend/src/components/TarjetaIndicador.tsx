interface Props {
  titulo: string
  valor: string // ya formateado; "—" cuando no hay dato
  nota?: string // aclaración pequeña debajo del número
}

// Una cifra grande con su nombre. Es un <div> dentro de una lista <dl> (término + valor).
export default function TarjetaIndicador({ titulo, valor, nota }: Props) {
  return (
    <div className="indicador">
      <dt>{titulo}</dt>
      <dd className="indicador-valor">{valor}</dd>
      {nota && <dd className="indicador-nota">{nota}</dd>}
    </div>
  )
}
