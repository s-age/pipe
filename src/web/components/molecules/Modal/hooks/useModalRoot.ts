// Module-level modal root creation. Keep it at module scope so it's created
// once when the module is imported (avoids reading refs during render).
const ID = 'modal-root'

let modalRoot = document.getElementById(ID) as HTMLElement | null
if (!modalRoot) {
  modalRoot = document.createElement('div')
  modalRoot.id = ID
  document.body.appendChild(modalRoot)
}

export const useModalRoot = (): HTMLElement | null => modalRoot
