'use client';

export function AnimatedGridBackground() {
    return (
        <div className="absolute inset-0 -z-10 h-full w-full bg-background overflow-hidden">
            <div className="absolute inset-0 bg-dot-white/[0.2]]"></div>
             <div className="absolute inset-0 flex items-center justify-center bg-background [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]"></div>
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2">
                <div className="h-[30rem] w-[30rem] rounded-full bg-primary/5 animate-[ripple_4s_infinite] [animation-delay:-2s]"></div>
                <div className="h-[50rem] w-[50rem] rounded-full bg-primary/5 animate-[ripple_4s_infinite] [animation-delay:-1s]"></div>
                <div className="h-[70rem] w-[70rem] rounded-full bg-primary/5 animate-[ripple_4s_infinite]"></div>
            </div>
        </div>
    );
}
