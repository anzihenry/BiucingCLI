export class CoreError extends Error {
  readonly code: number;
  constructor(code: number, message: string) { super(message); this.code = code; }
}
export class Cancellation {
  private requested: boolean = false;
  private listeners: Array<() => void> = [];
  get cancelled(): boolean { return this.requested; }
  cancel(): void {
    if (this.requested) { return; }
    this.requested = true;
    this.listeners.slice().forEach((listener: () => void) => listener());
  }
  subscribe(listener: () => void): () => void {
    if (this.requested) { listener(); return () => {}; }
    this.listeners.push(listener);
    return () => { this.listeners = this.listeners.filter((item: () => void) => item !== listener); };
  }
}
// Decimal strings preserve the full signed 64-bit range across ArkTS and C.
export interface AnalysisService {
  analyze(values: string[], cancellation?: Cancellation): Promise<string>;
  close(): Promise<void>;
}
export interface SessionFactory { create(): AnalysisService; }
export enum HomeOutput { OpenSettings }
export enum DeviceProfile { Mobile, Desktop, Watch, TV }
export class FeatureStyle {
  title: string = 'Shared core';
  action: string = 'Calculate 20 + 22';
}

export { BiucingColors, BiucingSpacing, BiucingRadius, BiucingTypography } from './DesignSystem';
