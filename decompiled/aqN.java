/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  gnu.trove.impl.hash.TLongHash
 *  gnu.trove.map.hash.TLongObjectHashMap
 */
import gnu.trove.impl.hash.TLongHash;
import gnu.trove.map.hash.TLongObjectHashMap;

class aqN
extends aqM<TLongObjectHashMap<int[]>> {
    aqN(aqH aqH2) {
        super(aqH2);
    }

    protected TLongObjectHashMap<int[]> tG(int n) {
        return new TLongObjectHashMap(n, 1.0f);
    }

    @Override
    protected void a(long l, aqH aqH2) {
        ((TLongObjectHashMap)this.cRi).put(l, (Object)aqH2.bGM());
    }

    @Override
    public int gw(long l) {
        int[] nArray = (int[])((TLongObjectHashMap)this.cRi).get(l);
        return nArray == null ? 0 : nArray.length;
    }

    @Override
    public int p(long l, int n) {
        return ((int[])((TLongObjectHashMap)this.cRi).get(l))[n];
    }

    @Override
    protected /* synthetic */ TLongHash tF(int n) {
        return this.tG(n);
    }
}
