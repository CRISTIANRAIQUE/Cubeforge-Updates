package br.minecraft.modcentral;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(ModCentral.MOD_ID)
public final class ModCentral {
    public static final String MOD_ID = "modcentral";
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MOD_ID);
    public static final RegistryObject<Item> ESPADA = ITEMS.register("espada_aetheric", () -> new SwordItem(Tiers.DIAMOND, 5, -2.4F, new Item.Properties()));
    public static final RegistryObject<Item> PICARETA = ITEMS.register("picareta_aetheric", () -> new PickaxeItem(Tiers.DIAMOND, 1, -2.8F, new Item.Properties()));
    public static final RegistryObject<Item> MACHADO = ITEMS.register("machado_aetheric", () -> new AxeItem(Tiers.DIAMOND, 6.0F, -3.0F, new Item.Properties()));
    public static final RegistryObject<Item> PA = ITEMS.register("pa_aetheric", () -> new ShovelItem(Tiers.DIAMOND, 1.5F, -3.0F, new Item.Properties()));
    public static final RegistryObject<Item> CRISTAL = ITEMS.register("cristal_aetheric", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> FRAGMENTO = ITEMS.register("fragmento_aetheric", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> LINGOTE = ITEMS.register("lingote_aetheric", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> NUCLEO = ITEMS.register("nucleo_aetheric", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> PEDRA = ITEMS.register("pedra_aetheric", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> EMBLEMA = ITEMS.register("emblema_mods", () -> new Item(new Item.Properties()));
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MOD_ID);
    public static final RegistryObject<CreativeModeTab> AETHERIC_TAB = TABS.register("mods",
        () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.modcentral.mods"))
            .icon(() -> new ItemStack(ESPADA.get()))
            .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
            .displayItems((parameters, output) -> {
                output.accept(ESPADA.get());
                output.accept(PICARETA.get());
                output.accept(MACHADO.get());
                output.accept(PA.get());
                output.accept(CRISTAL.get());
                output.accept(FRAGMENTO.get());
                output.accept(LINGOTE.get());
                output.accept(NUCLEO.get());
                output.accept(PEDRA.get());
                output.accept(EMBLEMA.get());
            })
            .build());
    public ModCentral() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(bus);
        TABS.register(bus);
    }
}
