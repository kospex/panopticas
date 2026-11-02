var target = Argument("target", "Default");
Task("Default").Does(() => Information("Hello"));
RunTarget(target);
