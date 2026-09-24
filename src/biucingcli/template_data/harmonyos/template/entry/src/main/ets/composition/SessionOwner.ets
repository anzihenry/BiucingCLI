import { HomeFactory, HomeModel } from '@biucing/homefeature';

// WindowStage owns this business session. Views borrow its model and never close it.
export class SessionOwner {
  readonly home: HomeModel;
  constructor(factory: HomeFactory) { this.home = factory.create(); }
  close(): Promise<void> { return this.home.close(); }
}
