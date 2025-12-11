import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import api from '../services/api'

const Publisher = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [presetId, setPresetId] = useState<number | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadedMedia, setUploadedMedia] = useState<any[]>([])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      setSelectedFiles((prev) => [...prev, ...acceptedFiles])
    },
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif'],
      'video/*': ['.mp4', '.mov'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
    },
  })

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return

    setLoading(true)
    try {
      const uploadPromises = selectedFiles.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        const response = await api.post('/publish/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        return response.data
      })

      const results = await Promise.all(uploadPromises)
      setUploadedMedia(results)
      setSelectedFiles([])
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePublish = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!presetId || uploadedMedia.length === 0) return

    setLoading(true)
    try {
      await api.post('/publish', {
        preset_id: presetId,
        media_id: uploadedMedia[0]?.id,
        title,
        description,
      })
      alert('Publication queued successfully!')
      setTitle('')
      setDescription('')
      setUploadedMedia([])
    } catch (error) {
      console.error('Publish failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Publisher</h1>
        <p className="mt-2 text-gray-400">Upload and publish content</p>
      </div>

      {/* File Upload */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Upload Media</h2>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-500/10'
              : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-gray-400">
            {isDragActive
              ? 'Drop files here...'
              : 'Drag & drop files here, or click to select'}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Supports: Images, Videos, Documents (PDF, DOCX)
          </p>
        </div>

        {selectedFiles.length > 0 && (
          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <p className="text-sm text-gray-400">
                {selectedFiles.length} file(s) selected
              </p>
              <button
                onClick={handleUpload}
                disabled={loading}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md text-sm disabled:opacity-50"
              >
                {loading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            <ul className="space-y-1">
              {selectedFiles.map((file, idx) => (
                <li key={idx} className="text-sm text-gray-300">
                  {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </li>
              ))}
            </ul>
          </div>
        )}

        {uploadedMedia.length > 0 && (
          <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded">
            <p className="text-green-500 text-sm">
              {uploadedMedia.length} file(s) uploaded successfully
            </p>
          </div>
        )}
      </div>

      {/* Publication Form */}
      <form onSubmit={handlePublish} className="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4">
        <h2 className="text-xl font-semibold text-white mb-4">Publication Details</h2>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Preset
          </label>
          <input
            type="number"
            value={presetId || ''}
            onChange={(e) => setPresetId(Number(e.target.value) || null)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
            placeholder="Preset ID"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
            placeholder="Publication title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
            placeholder="Publication description"
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || uploadedMedia.length === 0}
            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Publishing...' : 'Publish'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default Publisher

