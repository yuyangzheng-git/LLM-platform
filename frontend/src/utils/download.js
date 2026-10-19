// Download a generated file without navigating away from the app.
//
// <a download> is ignored for cross-origin URLs (generated images and
// videos are usually hosted elsewhere), and clicking such a link would
// replace the app with the file. Fetch it as a blob instead; if the host
// does not allow that (CORS), open it in a new tab.
export async function downloadFile(url, filename) {
  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    const objectUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000)
    return 'downloaded'
  } catch {
    window.open(url, '_blank', 'noopener,noreferrer')
    return 'opened'
  }
}
