'use client'

import React from 'react'

interface ConfirmModalProps {
  isOpen: boolean
  title: string
  message: string
  fileName?: string
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  cancelText?: string
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  fileName,
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
}: ConfirmModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative z-10 w-full max-w-lg p-6 card">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold" style={{ color: 'var(--mimic-text-dark, #0f172a)' }}>{title}</h3>
            <p className="text-sm mt-1" style={{ color: 'var(--mimic-muted)' }}>{fileName}</p>
          </div>
          <button onClick={onCancel} className="opacity-60 hover:opacity-90" style={{ color: 'var(--mimic-text-dark, #0f172a)' }}>✕</button>
        </div>
        <div className="mt-4 text-sm" style={{ color: 'var(--mimic-text-dark, #0f172a)' }}>{message}</div>
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onCancel} className="px-4 py-2 rounded-lg border border-gray-200 text-on-light">{cancelText}</button>
          <button onClick={onConfirm} className="px-4 py-2 rounded-lg text-white font-semibold btn-mimic" style={{ background: 'linear-gradient(90deg,var(--mimic-green-600),var(--mimic-green-500))' }}>{confirmText}</button>
        </div>
      </div>
    </div>
  )
}
