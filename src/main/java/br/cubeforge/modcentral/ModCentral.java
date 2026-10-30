package br.cubeforge.modcentral;

import net.fabricmc.api.ModInitializer;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.SoundType;

public final class ModCentral implements ModInitializer {
    public static final String ID = "modcentral";

    private static Identifier id(String name) {
        return Identifier.fromNamespaceAndPath(ID, name);
    }

    private static Item registerItem(String name, Item.Properties properties) {
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, id(name));
        return Registry.register(BuiltInRegistries.ITEM, key, new Item(properties.setId(key)));
    }

    private static Block registerOre(String name, float hardness) {
        Identifier identifier = id(name);
        ResourceKey<Block> blockKey = ResourceKey.create(Registries.BLOCK, identifier);
        Block ore = Registry.register(BuiltInRegistries.BLOCK, blockKey, new Block(
            BlockBehaviour.Properties.of()
                .setId(blockKey)
                .strength(hardness, 6.0f)
                .sound(SoundType.STONE)
                .requiresCorrectToolForDrops()
        ));
        ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, identifier);
        Registry.register(BuiltInRegistries.ITEM, itemKey,
                new BlockItem(ore, new Item.Properties().useBlockDescriptionPrefix().setId(itemKey)));
        return ore;
    }

    public static final Item CRISTAL = registerItem("cristal_azul", new Item.Properties());
    public static final Block MINERIO = registerOre("minerio_cristal_azul", 3.2f);
    public static final Block MINERIO_PROFUNDO = registerOre("minerio_cristal_profundo", 4.5f);

    private static ResourceKey<Item> swordKey() {
        return ResourceKey.create(Registries.ITEM, id("espada_cristal_azul"));
    }

    public static final Item ESPADA = Registry.register(BuiltInRegistries.ITEM, swordKey(),
        new Item(new Item.Properties().setId(swordKey())
            .sword(ToolMaterial.DIAMOND, 4.0f, -2.4f)));

    public static final ResourceKey<CreativeModeTab> TAB_KEY =
        ResourceKey.create(BuiltInRegistries.CREATIVE_MODE_TAB.key(), id("minerios_espadas"));

    public static final CreativeModeTab TAB = CreativeModeTab.builder()
        .title(Component.translatable("creativeTab.modcentral.minerios_espadas"))
        .icon(() -> new ItemStack(ESPADA))
        .displayItems((parameters, output) -> {
            output.accept(MINERIO);
            output.accept(MINERIO_PROFUNDO);
            output.accept(CRISTAL);
            output.accept(ESPADA);
        })
        .build();

    @Override
    public void onInitialize() {
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, TAB_KEY, TAB);
    }
}
