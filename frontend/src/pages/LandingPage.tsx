import HeroSection from "../components/landing/HeroSection";
import AboutSection from "../components/landing/AboutSection";
import FeaturedSection from "../components/landing/FeaturedSection";
import PhilosophySection from "../components/landing/PhilosophySection";
import CapabilitiesSection from "../components/landing/CapabilitiesSection";

export default function LandingPage() {
  return (
    <div className="bg-black">
      <HeroSection />
      <AboutSection />
      <FeaturedSection />
      <PhilosophySection />
      <CapabilitiesSection />
    </div>
  );
}
