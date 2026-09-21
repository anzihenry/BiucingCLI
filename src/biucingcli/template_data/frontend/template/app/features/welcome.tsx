import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { project } from "@/lib/project";
import { useHydrated } from "@/lib/use-hydrated";

export function Welcome() {
  const hydrated = useHydrated();
  const [count, setCount] = useState(0);
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <p className="text-sm text-muted-foreground">
          React Router · TypeScript · Tailwind
        </p>
        <h1 className="text-3xl font-semibold tracking-tight break-words">
          {project.title}
        </h1>
        <p className="text-muted-foreground">
          Your independent frontend starts here.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button
          disabled={!hydrated}
          onClick={() => setCount((current) => current + 1)}
        >
          Count: {count}
        </Button>
        <Dialog>
          <DialogTrigger
            disabled={!hydrated}
            render={<Button variant="outline" />}
          >
            About this starter
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Ready to build</DialogTitle>
              <DialogDescription>
                Accessible shadcn/ui components, typed routes, and a shared
                quality toolchain.
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      </div>
    </section>
  );
}
