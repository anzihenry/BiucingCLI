package {{PACKAGE_NAME}}.feature.home;

import dagger.BindsInstance;
import dagger.Component;
import dagger.Module;
import dagger.Provides;
import {{PACKAGE_NAME}}.core.model.AnalysisService;

// Generated and compiled at SDK publication. No Dagger types in the public factory API.
final class HomeAssembly {
    @Module static final class Bindings {
        @Provides static HomeModel model(AnalysisService service) { return new HomeModel(service); }
    }
    @Component(modules = Bindings.class) interface Graph {
        HomeModel model();
        @Component.Factory interface Factory {
            Graph create(@BindsInstance AnalysisService service);
        }
    }
    static HomeModel make(AnalysisService service) {
        return DaggerHomeAssembly_Graph.factory().create(service).model();
    }
}
