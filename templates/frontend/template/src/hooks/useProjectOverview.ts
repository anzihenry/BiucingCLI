import { useEffect, useState } from "react";

import { getProjectOverview } from "../services/projectOverview";
import type { ProjectOverview } from "../types/projectOverview";

export function useProjectOverview() {
  const [overview, setOverview] = useState<ProjectOverview | null>(null);

  useEffect(() => {
    setOverview(getProjectOverview());
  }, []);

  return overview;
}
