import { useContext } from 'react'
import { ToastContext } from '../../contexts/toastContext'

export function useToast() {
  return useContext(ToastContext)
}
