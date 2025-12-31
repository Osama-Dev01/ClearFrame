import { createContext } from 'react'
export const SBE = createContext({})
// The SBE context is used to share the state object { tb: 5000, te: 3400, s: 1600 } and its setter function
// across your entire application without prop drilling, making these values globally accessible to any 
 // component that needs them.