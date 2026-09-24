import { SessionFactory } from '@biucing/contracts';
import { SharedCoreFactory } from '@biucing/sharedcore';
export class Application {
  readonly sessions: SessionFactory = new SharedCoreFactory();
}
