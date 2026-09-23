package {{PACKAGE_NAME}};

import dagger.Component;
import dagger.Module;
import dagger.Provides;
import javax.inject.Singleton;
import {{PACKAGE_NAME}}.core.network.AppEnvironmentProvider;
import {{PACKAGE_NAME}}.core.network.DefaultAppEnvironmentProvider;
import {{PACKAGE_NAME}}.feature.home.HomeFactory;

final class ShellAssembly {
    @Module static final class Bindings {
        @Provides @Singleton static NativeAnalysisService service() { return new NativeAnalysisService(); }
        @Provides static HomeFactory home(NativeAnalysisService service) { return new HomeFactory(service); }
        @Provides static AppEnvironmentProvider environment() { return new DefaultAppEnvironmentProvider(); }
    }
    // Each create call constructs an isolated session graph, never an application-wide mutable session.
    @Singleton @Component(modules = Bindings.class) interface Graph {
        NativeAnalysisService service();
        HomeFactory home();
        AppEnvironmentProvider environment();
    }
    static Graph session() { return DaggerShellAssembly_Graph.create(); }
}
