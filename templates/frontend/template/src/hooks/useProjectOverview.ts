import { useEffect, useState } from "react";

import { getProjectOverview } from "../services/projectOverview";
import type { ProjectOverview } from "../types/projectOverview";

export function useProjectOverview() {
  const [overview, setOverview] = useState<ProjectOverview | null>(null);

  useEffect(() => {
    let isMounted = true;

    void getProjectOverview().then((data) => {
      if (isMounted) {
        setOverview(data);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  return overview;
}
