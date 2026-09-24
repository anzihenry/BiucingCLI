import { SessionFactory } from '@biucing/contracts';
import { SharedCoreFactory } from '@biucing/sharedcore';
import { createHomeFactory } from './GeneratedGraph';
import { SessionOwner } from './SessionOwner';

export class Application {
  private sessions: SessionFactory;
  constructor(sessions: SessionFactory = new SharedCoreFactory()) { this.sessions = sessions; }
  createSession(): SessionOwner { return new SessionOwner(createHomeFactory(this.sessions)); }
}
