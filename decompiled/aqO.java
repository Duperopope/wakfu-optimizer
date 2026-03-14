/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  gnu.trove.impl.hash.TLongHash
 *  gnu.trove.map.hash.TLongObjectHashMap
 */
import gnu.trove.impl.hash.TLongHash;
import gnu.trove.map.hash.TLongObjectHashMap;

class aqO
extends aqM<TLongObjectHashMap<Integer>> {
    aqO(aqH aqH2) {
        super(aqH2);
    }

    protected TLongObjectHashMap<Integer> tG(int n) {
        return new TLongObjectHashMap(n, 1.0f);
    }

    @Override
    protected void a(long l, aqH aqH2) {
        ((TLongObjectHashMap)this.cRi).put(l, (Object)aqH2.bGI());
    }

    @Override
    public int gw(long l) {
        return ((TLongObjectHashMap)this.cRi).contains(l) ? 1 : 0;
    }

    @Override
    public int p(long l, int n) {
        return (Integer)((TLongObjectHashMap)this.cRi).get(l);
    }

    @Override
    protected /* synthetic */ TLongHash tF(int n) {
        return this.tG(n);
    }
}
