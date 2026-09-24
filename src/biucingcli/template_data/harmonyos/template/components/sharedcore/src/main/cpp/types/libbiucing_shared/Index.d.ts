export interface NativeSession { readonly brand: string; }
export const create: () => NativeSession;
export const analyze: (session: NativeSession, values: string[]) => Promise<string>;
export const cancel: (session: NativeSession) => void;
export const close: (session: NativeSession) => void;
