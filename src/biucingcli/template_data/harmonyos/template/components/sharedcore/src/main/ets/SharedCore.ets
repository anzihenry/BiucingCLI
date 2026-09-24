import nativeCore, { NativeSession } from 'libbiucing_shared.so';
import { AnalysisService, SessionFactory, Cancellation, CoreError } from '@biucing/contracts';

class CoreSession implements AnalysisService {
  private handle: NativeSession = nativeCore.create();
  private tail: Promise<void> = Promise.resolve();
  private closing: boolean = false;
  private closed: Promise<void> | undefined = undefined;
  analyze(values: string[], cancellation: Cancellation = new Cancellation()): Promise<string> {
    if (this.closing) { return Promise.reject(new CoreError(4, 'Session closed')); }
    const input: string[] = values.slice();
    const result: Promise<string> = this.tail.then(async (): Promise<string> => {
      if (this.closing) { throw new CoreError(4, 'Session closed'); }
      if (cancellation.cancelled) { throw new CoreError(3, 'Cancelled'); }
      const pending: Promise<string> = nativeCore.analyze(this.handle, input);
      const unsubscribe = cancellation.subscribe(() => nativeCore.cancel(this.handle));
      try { return await pending; } finally { unsubscribe(); }
    });
    this.tail = result.then(() => {}, () => {});
    return result;
  }
  close(): Promise<void> {
    if (this.closed) { return this.closed; }
    this.closing = true;
    nativeCore.cancel(this.handle);
    this.closed = this.tail.then(() => nativeCore.close(this.handle));
    return this.closed;
  }
}
export class SharedCoreFactory implements SessionFactory {
  create(): AnalysisService { return new CoreSession(); }
}
