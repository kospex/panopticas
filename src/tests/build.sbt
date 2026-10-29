ThisBuild / scalaVersion := "3.3.4"

lazy val root = (project in file("."))
  .settings(
    name := "example",
    libraryDependencies += "org.scalameta" %% "munit" % "1.0.2" % Test
  )
