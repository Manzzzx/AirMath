export default function ResultBox({ expr, result }: { expr: string; result: string }) {
  return (
    <div className="mt-4 p-4 border rounded-xl bg-gray-100">
      <p><strong>Ekspresi:</strong> {expr || '...'}</p>
      <p><strong>Hasil:</strong> {result || '...'}</p>
    </div>
  )
}
